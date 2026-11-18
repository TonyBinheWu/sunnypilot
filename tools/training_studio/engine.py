"""Resumable stage runner. A new dataset creates a new version; failures never spin optimizers."""
import argparse
from contextlib import contextmanager
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request

from tools.training_studio.store import BASE, STAGES, Store, exclusive_worker, read_json, write_json
from openpilot.sunnypilot.formosalink.training_protocol import digest_file

TEACHER_REVISION = "b92b6aa326bd3e2235db28f248ad5a30b5890e64"


@contextmanager
def worker_heartbeat(store, interval=2):
  """Report liveness independently of slow network transfers and dataset hashing."""
  done=threading.Event()
  lock=threading.Lock()
  current={'state':'starting'}
  def publish(**fields):
    with lock:
      current.clear()
      current.update(fields)
      write_json(store.root/'worker.json',{'pid':os.getpid(),'updated':time.time(),**current})
  def run():
    while not done.wait(interval):
      with lock:
        write_json(store.root/'worker.json',{'pid':os.getpid(),'updated':time.time(),**current})
  publish(state='starting')
  thread=threading.Thread(target=run,name='studio-heartbeat',daemon=True)
  thread.start()
  try:
    yield publish
  finally:
    done.set()
    thread.join()
    publish(state='stopped')


def base_model(store):
  path = store.root / "models" / "n16.onnx"
  if not path.is_file() or path.stat().st_size != BASE["size"] or digest_file(path) != BASE["sha256"]:
    raise RuntimeError("verified N16 base absent; run fetch-model first")
  return path


def fetch_model(store):
  path = store.root / "models" / "n16.onnx"
  path.parent.mkdir(exist_ok=True)
  if not path.is_file():
    url = f"https://huggingface.co/{BASE['repository']}/resolve/{BASE['revision']}/{BASE['path']}"
    request = urllib.request.Request(url, headers={"User-Agent":"FormosaPilot-Training-Studio/1"})
    temporary = path.with_suffix(".part")
    with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
      shutil.copyfileobj(response,output,1024*1024)
    if temporary.stat().st_size != BASE["size"] or digest_file(temporary) != BASE["sha256"]:
      raise ValueError("downloaded N16 failed size/hash verification")
    os.replace(temporary,path)
  base_model(store)
  import onnx
  import math
  model = onnx.load(str(path))
  contract = {"inputs":{value.name:[dim.dim_value for dim in value.type.tensor_type.shape.dim] for value in model.graph.input},
              "outputs":{value.name:[dim.dim_value for dim in value.type.tensor_type.shape.dim] for value in model.graph.output}}
  receipt = {**BASE,"verified":True,"initializer_parameters":sum(math.prod(value.dims) for value in model.graph.initializer),
    "contract":contract,"verified_at":time.time(),"source":"carrot-wip N16 Nav catalog"}
  write_json(path.parent/"base.json",receipt)
  store.event("N16 基底已驗證並完成張量契約提取")
  return receipt


def teacher(folder):
  import numpy as np
  from tools.training_studio import plan_head
  folder = Path(folder)
  plan = read_json(folder/"plan.json")
  config = plan["config"]
  url = config.get("teacher_url","http://127.0.0.1:18766").rstrip("/")
  opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with opener.open(url+"/health",timeout=30) as response:
    health = json.load(response)
  provenance = health.get("provenance",{})
  if (not health.get("teacher_ready") or provenance.get("revision") != TEACHER_REVISION
      or provenance.get("weights_verified") is not True or provenance.get("camera_ids")!=[1,6]):
    raise ValueError("pinned Alpamayo 2 Edge teacher unavailable")
  qualification = read_json(config.get("teacher_qualification","")) if config.get("teacher_qualification") else None
  if not qualification or qualification.get("passed") is not True or qualification.get("provenance") != provenance:
    raise ValueError("this exact front-only teacher requires a matching closed-loop qualification receipt")
  if qualification.get("input_profile") != "experimental_front_only" or not qualification.get("cases"):
    raise ValueError("front-only teacher qualification is incomplete")
  prepared = read_json(folder/"prepared.json")
  rows, rejected = [], []
  labels = folder/"labels"
  labels.mkdir()
  for index,row in enumerate(prepared["samples"]):
    payload = (folder/"packets"/(row["id"]+".npz")).read_bytes()
    request = urllib.request.Request(url+"/predict",data=payload,headers={"Content-Type":"application/octet-stream"})
    with opener.open(request,timeout=float(config.get("teacher_timeout_s",180))) as response:
      result = json.load(response)
    write_json(labels/(row["id"]+".json"),result)
    if result.get("backend") != "nvidia_alpamayo2_edge" or result.get("teacher_revision") != TEACHER_REVISION or result.get("scripted_fallback") is not False or result.get("diagnostic_only"):
      raise ValueError("teacher provenance changed or diagnostic labels supplied")
    import hashlib
    if result.get("ok") is not True or result.get("input_sha256")!=hashlib.sha256(payload).hexdigest():
      raise ValueError("teacher response does not match this observed input")
    actions = np.asarray(result.get("actions_accel_curvature"),np.float32)
    xyz = np.asarray(result.get("xyz"),np.float32)
    if actions.shape != (64,2) or xyz.shape != (64,3) or not np.isfinite(actions).all() or not np.isfinite(xyz).all():
      raise ValueError("invalid teacher trajectory/action shapes")
    uncertain = any(term in result.get("cot","").lower() for term in config.get("uncertainty_terms",["cannot determine","highly uncertain","視線遮擋"]))
    if uncertain or abs(actions[:,0]).max()>12 or abs(actions[:,1]).max()>.5 or row["speed"]>float(config.get("max_speed_mps",15)):
      rejected.append(row["id"])
      continue
    # Teacher FLU curvature -> N16 FRD lateral-acceleration action. Match action_t [.2,.3].
    lateral = -float(np.interp(.2,np.arange(1,65)*.1,actions[:,1]))*max(float(config.get("action_speed_floor_mps",2.5)),row["speed"])**2
    acceleration = float(np.interp(.3,np.arange(1,65)*.1,actions[:,0]))
    rows.append({**row,"target":[lateral,acceleration],"plan_target":plan_head.targets(result,row["speed"])})
    write_json(folder/"progress.json",{"stage":"teacher","done":index+1,"total":len(prepared["samples"]),"accepted":len(rows),"rejected":len(rejected),"updated":time.time()})
  if not rows:
    raise ValueError("teacher produced no qualified labels")
  with opener.open(url+"/health",timeout=30) as response:
    if json.load(response).get("provenance")!=provenance:
      raise ValueError("teacher changed during labeling; refusing a mixed-checkpoint dataset")
  np.savez_compressed(folder/"dataset.npz",**{key:np.asarray([row[source] for row in rows]) for key,source in
    (("features","features"),("context","context"),("target","target"),("split","split"),("group","group"),
     ("source_action","source_action"),("plan_features","plan_features"),("plan_target","plan_target"))})
  write_json(folder/"teacher.json",{"model":"nvidia/Alpamayo2-Edge","revision":TEACHER_REVISION,"provenance":provenance,
    "qualification":qualification,"accepted":len(rows),"rejected":rejected,"pseudo_labels":True,"latent_distillation":False,
    "coordinates":"FLU teacher -> FRD N16; lateral=-curvature*max(speed_floor,v)^2",
    "action_speed_floor_mps":float(config.get("action_speed_floor_mps",2.5)),"dataset_sha256":digest_file(folder/"dataset.npz")})


def evaluate(folder):
  import numpy as np
  import onnx
  import torch
  from tools.training_studio.head import network_from
  from tools.training_studio import plan_head
  folder = Path(folder)
  training = read_json(folder/"training.json")
  model=onnx.load(str(folder/"candidate.onnx"))
  network = network_from(model)
  trajectory_network=plan_head.network_from(model)
  data = np.load(folder/"dataset.npz",allow_pickle=False)
  mask = data["split"] == "test"
  if not mask.any():
    raise ValueError("held-out test routes unavailable")
  with torch.no_grad():
    prediction = network(torch.from_numpy(data["features"][mask]).float(),torch.from_numpy(data["context"][mask]).float()).numpy()
    trajectory=trajectory_network(torch.from_numpy(data["plan_features"][mask]).float()).numpy()
  mse = float(np.square(prediction-data["target"][mask]).mean())
  validation_passed = training["final"]["validation"] <= training["baseline"]["validation"]
  write_json(folder/"evaluation.json",{"candidate_sha256":training["candidate_sha256"],"snapshot":training["snapshot"],
    "validation_passed":validation_passed,"test_samples":int(mask.sum()),"test_action_mse":mse,
    "test_trajectory_position_rmse_m":float(np.sqrt(np.square(trajectory[...,:3]-data["plan_target"][mask,...,:3]).mean())),
    "closed_loop_passed":False,"device_passed":False,"publishable":False,"reason":"尚待閉迴路回歸與 RX 9060 實機驗收"})
  if not validation_passed:
    raise ValueError("validation regressed; candidate cannot become a continual-training parent")


def compile_candidate(folder):
  plan = read_json(Path(folder)/"plan.json")
  command = plan["config"].get("compiler_command")
  if not command:
    return False
  if not isinstance(command,list) or not command or any(not isinstance(argument,str) for argument in command):
    raise ValueError("compiler_command must be an argument array")
  subprocess.run([argument.replace("{run}",str(Path(folder).resolve())) for argument in command],check=True)
  artifact = Path(folder)/"release"/"big_driving_tinygrad.pkl"
  receipt = read_json(Path(folder)/"compile.json",{})
  if not artifact.is_file() or receipt.get("onnx_sha256") != digest_file(Path(folder)/"candidate.onnx") or receipt.get("artifact_sha256") != digest_file(artifact):
    raise ValueError("compiler did not produce a bound artifact/receipt")
  return True


def stage(name, folder):
  if name == "prepare":
    from tools.training_studio.prepare import prepare
    prepare(folder)
  elif name == "teacher":
    teacher(folder)
  elif name == "train":
    if read_json(Path(folder)/"plan.json")["config"].get("remote"):
      from tools.training_studio.remote import train
    else:
      from tools.training_studio.head import train
    train(folder)
  elif name == "evaluate":
    evaluate(folder)
  elif name == "compile":
    compile_candidate(folder)
  else:
    raise ValueError("unknown stage")


def worker(root, stop=None):
  store = Store(root)
  stop = stop or threading.Event()
  with exclusive_worker(root), worker_heartbeat(store) as heartbeat:
    # Restarted interrupted optimizers need inspection, not an automatic second start.
    with store.db() as db:
      db.execute("UPDATE jobs SET state='interrupted',error='worker restarted; explicit retry creates a new version' WHERE state='running'")
    child = None
    collector_error = None
    try:
      while not stop.is_set():
        heartbeat(state='watching' if store.enabled() else 'paused')
        scan = store.root/"scan-request.json"
        if scan.exists():
          scan.unlink()
          store.discover()
        if not store.enabled():
          stop.wait(2)
          continue
        if store.config().get("collector"):
          try:
            heartbeat(state='collecting')
            from tools.training_studio.collector import sync
            sync(store,stop=stop)
            collector_error=None
          except Exception as exc:
            if str(exc)!=collector_error:
              store.event("資料同步等待："+str(exc))
              collector_error=str(exc)
        heartbeat(state='importing')
        store.discover()
        store.enqueue()
        with store.db() as db:
          db.execute("BEGIN IMMEDIATE")
          row = db.execute("SELECT * FROM jobs WHERE state='queued' ORDER BY created LIMIT 1").fetchone()
          if row:
            db.execute("UPDATE jobs SET state='running',updated=? WHERE id=?",(time.time(),row["id"]))
        if not row:
          heartbeat(state='watching')
          stop.wait(5)
          continue
        identity = row["id"]
        folder = store.root/"runs"/identity
        try:
          source = base_model(store)
          if row["parent"]:
            parent = store.root/"runs"/row["parent"]
            source = parent/"candidate.onnx"
            if digest_file(source) != read_json(parent/"training.json")["candidate_sha256"]:
              raise ValueError("parent digest changed")
          shutil.copyfile(source,folder/"source.onnx")
          for name in STAGES:
            if not store.enabled() or stop.is_set():
              raise InterruptedError("paused by user")
            store.update(identity,"running",name)
            store.event("開始階段："+name,identity)
            with (folder/(name+".log")).open("a",encoding="utf-8") as log:
              child = subprocess.Popen([sys.executable,"-m","tools.training_studio.engine","stage",name,"--run",str(folder)],
                stdout=log,stderr=subprocess.STDOUT,start_new_session=os.name!="nt")
              while child.poll() is None:
                if not store.enabled() or stop.wait(1):
                  if os.name!="nt":
                    os.killpg(child.pid,signal.SIGTERM)
                  else:
                    child.terminate()
                  try:
                    child.wait(timeout=10)
                  except subprocess.TimeoutExpired:
                    if os.name!="nt":
                      os.killpg(child.pid,signal.SIGKILL)
                    else:
                      child.kill()
                    child.wait()
                  raise InterruptedError("paused; no automatic optimizer restart")
                heartbeat(state=name,job=identity)
              if child.returncode:
                tail = (folder/(name+".log")).read_text(encoding="utf-8",errors="replace")[-2000:]
                raise RuntimeError(name+" failed: "+tail)
              child = None
          compiled = (folder/"compile.json").is_file()
          store.update(identity,"completed","awaiting_device_acceptance" if not compiled else "awaiting_publication")
          store.event("訓練版本完成；發布仍需驗收與手動選擇",identity)
        except InterruptedError as exc:
          store.update(identity,"interrupted","paused",str(exc))
        except Exception as exc:
          store.update(identity,"failed",name if "name" in locals() else "prepare",str(exc))
          store.event(str(exc),identity)
    finally:
      if child and child.poll() is None:
        child.terminate()
        child.wait(timeout=10)
      heartbeat(state='stopped')


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  commands = parser.add_subparsers(dest="command",required=True)
  for name in ("worker","fetch-model"):
    sub = commands.add_parser(name)
    sub.add_argument("--root",required=True)
  sub = commands.add_parser("stage")
  sub.add_argument("stage",choices=STAGES)
  sub.add_argument("--run",required=True)
  args = parser.parse_args()
  if args.command == "stage":
    stage(args.stage,Path(args.run))
  elif args.command == "fetch-model":
    print(json.dumps(fetch_model(Store(args.root))))
  else:
    stop = threading.Event()
    for signum in (signal.SIGINT,signal.SIGTERM):
      signal.signal(signum,lambda *_:stop.set())
    worker(args.root,stop)


if __name__ == "__main__":
  main()
