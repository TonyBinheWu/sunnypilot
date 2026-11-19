"""Transfer bound training snapshots to DGX and supervise only our own training container."""
import io
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import tarfile
import threading
import time

from tools.training_studio.store import read_json, write_json
from openpilot.sunnypilot.formosalink.training_protocol import digest_file


class Remote:
  def __init__(self,config):
    self.config=config
    self.host=config["host"]
    self.root=config["workspace"]
    self.image=config["image"]
    if not re.fullmatch(r"[A-Za-z0-9_.@:-]+",self.host) or not re.fullmatch(r"/[A-Za-z0-9_./-]+",self.root) or ".." in Path(self.root).parts:
      raise ValueError("invalid DGX host/workspace")
    if not re.fullmatch(r"[A-Za-z0-9_./:@-]+",self.image):
      raise ValueError("invalid pinned DGX image")
    self.ssh=config.get("ssh_command",["ssh","-o","BatchMode=yes"])
    if not isinstance(self.ssh,list) or not all(isinstance(value,str) for value in self.ssh):
      raise ValueError("ssh_command must be an argument array")

  def command(self,command):
    return [*self.ssh,self.host,command]

  def call(self,command,**kwargs):
    return subprocess.run(self.command(command),check=True,timeout=kwargs.pop("timeout",60),**kwargs)

  def program(self, snapshot=False):
    root=Path(__file__).resolve().parents[2]
    buffer=io.BytesIO()
    files=["tools/training_studio/__init__.py","tools/training_studio/head.py","tools/training_studio/plan_head.py","tools/training_studio/store.py",
           "tools/training_studio/remote_head.py","tools/training_studio/teacher_reasoning_train.py","tools/training_studio/teacher_train.py","tools/training_studio/teacher_lora.py","tools/training_studio/teacher_optim.py","tools/training_studio/teacher_route_data.py","tools/training_studio/teacher_replay.py",
           "tools/training_studio/teacher_service.py","tools/training_studio/teacher_motion.py","tools/training_studio/teacher_forward_motion.py","tools/training_studio/teacher_standstill.py","tools/training_studio/edge_inputs.py","openpilot/sunnypilot/formosalink/training_protocol.py"]
    fingerprint=hashlib.sha256()
    with tarfile.open(fileobj=buffer,mode="w:gz") as archive:
      for name in files:
        body=(root/name).read_bytes()
        fingerprint.update(name.encode()+b'\0'+body)
        member=tarfile.TarInfo(name)
        member.size=len(body)
        archive.addfile(member,io.BytesIO(body))
    program=self.root+"/program"
    if snapshot: program+='-'+fingerprint.hexdigest()[:16]
    self.call("mkdir -p "+shlex.quote(program)+" && tar -xzf - -C "+shlex.quote(program),input=buffer.getvalue())
    return program

  def upload(self,source,destination):
    with Path(source).open("rb") as stream:
      self.call("cat > "+shlex.quote(destination+".part")+" && mv "+shlex.quote(destination+".part")+" "+shlex.quote(destination),stdin=stream,timeout=1800)

  def download(self,source,destination):
    destination=Path(destination)
    with destination.with_suffix(destination.suffix+".part").open("wb") as stream:
      self.call("cat "+shlex.quote(source),stdout=stream,timeout=1800)
    os.replace(destination.with_suffix(destination.suffix+".part"),destination)

  def setup(self):
    self.program()
    # Dependencies are isolated from the running Alpamayo container and its Python environment.
    command=["docker","run","--rm","-v",self.root+":/studio",self.image,"python","-m","pip","install","--target","/studio/deps",
      "onnx>=1.18,<2","onnxruntime>=1.23,<2"]
    probe=["docker","run","--rm","--gpus","all","--network","none","-v",self.root+":/studio",self.image,
      "env","PYTHONPATH=/studio/deps:/studio/program","python","-c",
      "import json,torch,onnx,onnxruntime; print(json.dumps({'cuda':torch.cuda.is_available(),'gpu':torch.cuda.get_device_name(0),'torch':torch.__version__,'onnx':onnx.__version__,'onnxruntime':onnxruntime.__version__}))"]
    try:
      return self.call(shlex.join(probe),capture_output=True,text=True,timeout=120).stdout
    except subprocess.CalledProcessError:
      self.call(shlex.join(command),timeout=600)
      return self.call(shlex.join(probe),capture_output=True,text=True,timeout=120).stdout


def train(folder):
  folder=Path(folder)
  config=read_json(folder/"plan.json")["config"]["remote"]
  remote=Remote(config)
  stop=threading.Event()
  for signum in (signal.SIGTERM,signal.SIGINT):
    signal.signal(signum,lambda *_:stop.set())
  remote.program()
  destination=remote.root+"/runs/"+folder.name
  cache=remote.root+"/models/"+digest_file(folder/"source.onnx")+".onnx"
  remote.call("mkdir -p "+shlex.quote(destination)+" "+shlex.quote(remote.root+"/models"))
  check=remote.call("if test -f "+shlex.quote(cache)+"; then sha256sum "+shlex.quote(cache)+"; fi",capture_output=True,text=True).stdout
  if not check.startswith(digest_file(folder/"source.onnx")):
    remote.upload(folder/"source.onnx",cache)
  remote.call("ln "+shlex.quote(cache)+" "+shlex.quote(destination+"/source.onnx"))
  for name in ("plan.json","dataset.npz","teacher.json"):
    remote.upload(folder/name,destination+"/"+name)
  if stop.is_set():
    raise InterruptedError("stopped before DGX optimizer start")
  container="studio-"+folder.name.lower()
  command=["docker","run","--rm","--name",container,"--gpus","all","--network","none","--memory","12g",
    "-v",remote.root+":/studio","-w","/studio",remote.image,"env","PYTHONPATH=/studio/deps:/studio/program",
    "python","-m","tools.training_studio.remote_head","--run","/studio/runs/"+folder.name]
  child=subprocess.Popen(remote.command(shlex.join(command)))
  try:
    while child.poll() is None:
      if stop.wait(3):
        remote.call(shlex.join(["docker","stop","--time","3",container]),timeout=15)
        child.wait(timeout=10)
        raise InterruptedError("owned DGX training container stopped")
      result=remote.call("if test -f "+shlex.quote(destination+"/progress.json")+"; then cat "+shlex.quote(destination+"/progress.json")+"; fi",capture_output=True,text=True)
      if result.stdout.strip():
        write_json(folder/"progress.json",json.loads(result.stdout))
    if child.returncode:
      raise RuntimeError("DGX training failed; see train.log")
  finally:
    if child.poll() is None:
      try:
        remote.call(shlex.join(["docker","stop","--time","3",container]),timeout=15)
      finally:
        child.terminate()
        child.wait(timeout=10)
  for name in ("training.json","progress.json","candidate.onnx"):
    remote.download(destination+"/"+name,folder/name)
  if digest_file(folder/"candidate.onnx") != read_json(folder/"training.json")["candidate_sha256"]:
    raise ValueError("DGX candidate transfer hash mismatch")


def main():
  import argparse
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument("command",choices=("setup","train"))
  parser.add_argument("--root")
  parser.add_argument("--run")
  args=parser.parse_args()
  if args.command=="setup":
    result=Remote(read_json(Path(args.root)/"config.json")["remote"]).setup()
    for line in reversed(result.splitlines()):
      try:
        status=json.loads(line)
        if "cuda" in status:
          write_json(Path(args.root)/"worker-readiness.json",{**status,"verified_at":time.time()})
          break
      except ValueError:
        pass
    print(result)
  else:
    train(args.run)


if __name__=="__main__":
  main()
