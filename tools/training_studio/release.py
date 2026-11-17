"""Bound acceptance receipts and manual immutable GitHub Release publication."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

from tools.training_studio.store import Store, read_json, write_json
from openpilot.sunnypilot.formosalink.training_protocol import digest_file, valid_hash


def run_folder(store, version):
  if not isinstance(version,str) or not re.fullmatch(r"n16-[A-Za-z0-9-]+",version):
    raise ValueError("invalid version")
  path = store.root/"runs"/version
  if not (path/"training.json").is_file():
    raise ValueError("training version unavailable")
  return path


def accept(store, version, closed_loop_path, device_path):
  folder = run_folder(store,version)
  checksum = digest_file(folder/"candidate.onnx")
  closed_loop, device = read_json(closed_loop_path), read_json(device_path)
  if not closed_loop or closed_loop.get("candidate_sha256") != checksum or closed_loop.get("passed") is not True or not closed_loop.get("cases"):
    raise ValueError("closed-loop acceptance must identify this exact candidate and recorded cases")
  for row in closed_loop["cases"]:
    if row.get("passed") is not True or not valid_hash(row.get("evidence_sha256")):
      raise ValueError("every closed-loop case requires passing bound evidence")
  if not device or device.get("candidate_sha256") != checksum or device.get("passed") is not True:
    raise ValueError("device acceptance must identify this exact candidate")
  numbers = (device.get("inference_p99_ms"),device.get("peak_vram_bytes"),device.get("model_hz"))
  import math
  if any(type(value) not in (int,float) or not math.isfinite(value) or value<0 for value in numbers):
    raise ValueError("finite measured device metrics required")
  if not (0<numbers[0]<25 and 0<numbers[1]<=3_000_000_000 and numbers[2]>=20):
    raise ValueError("RX 9060 latency/memory/frequency acceptance failed")
  if device.get("gpu_arch") != "gfx1200" or device.get("gpu_model") != "AMD Radeon RX 9060" or device.get("precision") != "FP16":
    raise ValueError("exact RX 9060 FP16 hardware acceptance required")
  if device.get("fallback_passed") is not True or device.get("thermal_soak_passed") is not True:
    raise ValueError("fallback and thermal acceptance required")
  evaluation = read_json(folder/"evaluation.json",{})
  if evaluation.get("candidate_sha256") != checksum or not evaluation.get("validation_passed"):
    raise ValueError("version validation missing or regressed")
  compiled = read_json(folder/"compile.json",{})
  artifact = folder/"release"/"big_driving_tinygrad.pkl"
  if not artifact.is_file() or compiled.get("onnx_sha256") != checksum or compiled.get("artifact_sha256") != digest_file(artifact):
    raise ValueError("matching eGPU compilation required before acceptance")
  if device.get("artifact_sha256") != compiled["artifact_sha256"]:
    raise ValueError("device tested a different compiled artifact")
  write_json(folder/"closed-loop-acceptance.json",closed_loop)
  write_json(folder/"device-acceptance.json",device)
  evaluation.update(closed_loop_passed=True,device_passed=True,publishable=True,
    acceptance={"closed_loop_sha256":digest_file(Path(closed_loop_path)),"device_sha256":digest_file(Path(device_path))},reason="驗收通過；可由操作者手動發布")
  write_json(folder/"evaluation.json",evaluation)
  store.event("版本通過閉迴路與 RX 9060 驗收，可手動推送",version)
  return evaluation


def validate_release(store,version):
  folder = run_folder(store,version)
  evaluation = read_json(folder/"evaluation.json",{})
  if not evaluation.get("publishable") or evaluation.get("candidate_sha256") != digest_file(folder/"candidate.onnx"):
    raise ValueError("此版本尚未通過綁定模型雜湊的閉迴路與實機驗收")
  manifest = read_json(folder/"release"/"manifest.json",{})
  artifact = folder/"release"/manifest.get("filename","missing")
  if not artifact.is_relative_to(folder/"release") or not artifact.is_file() or manifest.get("sha256") != digest_file(artifact) or manifest.get("size") != artifact.stat().st_size:
    raise ValueError("release artifact mismatch")
  precompiled = read_json(folder/"release"/"precompiled.json",{})
  runtime = folder/"release"/"precompiled-runtime.tar.gz"
  if not runtime.is_file() or precompiled.get("runtime",{}).get("sha256") != digest_file(runtime):
    raise ValueError("matching pinned tinygrad runtime required")
  if precompiled.get("pickle",{}).get("sha256") != manifest["sha256"] or precompiled.get("model_sha256") != manifest["sha256"]:
    raise ValueError("precompiled manifest artifact mismatch")
  return folder


def request_publish(store,version):
  folder = validate_release(store,version)
  state = read_json(folder/"release.json",{})
  if state.get("published") or (folder/"publish-request.json").exists():
    raise ValueError("此版本已推送或正在推送；請查看發布紀錄")
  path = folder/"publish-request.json"
  with path.open("x",encoding="utf-8") as stream:
    json.dump({"requested":time.time()},stream)
  with (folder/"publish.log").open("a",encoding="utf-8") as log:
    child = subprocess.Popen([sys.executable,"-m","tools.training_studio.release","publish","--root",str(store.root),"--version",version],
      stdout=log,stderr=subprocess.STDOUT,start_new_session=os.name!="nt")
  return {"queued":True,"pid":child.pid,"version":version}


def credential():
  value = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
  if value:
    return value
  # Existing Git authentication stays in memory; never log or persist the credential.
  result = subprocess.run(["git","credential","fill"],input="protocol=https\nhost=github.com\n\n",text=True,capture_output=True,
    timeout=30,env={**os.environ,"GIT_TERMINAL_PROMPT":"0","GCM_INTERACTIVE":"Never"})
  fields = dict(line.split("=",1) for line in result.stdout.splitlines() if "=" in line)
  if result.returncode or not fields.get("password"):
    raise ValueError("GitHub 發布認證不可用；請先登入 Git credential manager 或設定工作程序的 GH_TOKEN")
  return fields["password"]


def publish(store,version):
  folder = validate_release(store,version)
  repository = store.config().get("release_repository","")
  if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",repository):
    raise ValueError("invalid release repository")
  token = credential()
  def request(url,method="GET",value=None,raw=None):
    data = raw if raw is not None else json.dumps(value).encode() if value is not None else None
    headers = {"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28",
      "User-Agent":"FormosaPilot-Training-Studio","Content-Type":"application/octet-stream" if raw is not None else "application/json"}
    try:
      with urllib.request.urlopen(urllib.request.Request(url,data=data,method=method,headers=headers),timeout=600) as response:
        return json.load(response)
    except urllib.error.HTTPError as exc:
      raise ValueError(f"GitHub {method} request failed: HTTP {exc.code}") from None
  endpoint="https://api.github.com/repos/"+repository+"/releases"
  if request("https://api.github.com/repos/"+repository).get("private") is not False:
    raise ValueError("車機匿名下載需要公開的模型發行倉庫；不會自動變更倉庫隱私設定")
  state = read_json(folder/"release.json",{})
  if state.get("published"):
    return state
  if state.get("release_id"):
    release = request(endpoint+"/"+str(state["release_id"]))
    if not release.get("draft"):
      raise ValueError("remote release is already immutable; reconcile before retrying")
  else:
    release = request(endpoint,"POST",{"tag_name":version,"target_commitish":store.config().get("release_branch","carrot-wip"),
      "name":"N16 distilled · "+version,"draft":True,"prerelease":True,
      "body":"Alpamayo 2 Edge action/residual distillation of N16 Nav. Visual backbone frozen. Includes version-bound validation and RX 9060 acceptance receipts."})
    state={"release_id":release["id"],"published":False,"tag":version,"repository":repository}
    write_json(folder/"release.json",state)
  for name in ("training.json","evaluation.json","closed-loop-acceptance.json","device-acceptance.json","compile.json"):
    # Only bounded reports and model artifacts are published; no raw logs, images, source paths or teacher reasoning.
    report = read_json(folder/name)
    if name == "training.json":
      report = {key:report[key] for key in ("base","source_sha256","candidate_sha256","snapshot","scope","backbone_frozen","trainable_parameters","changed_parameters","baseline","final","history","export_parity","device","epochs")}
    write_json(folder/"release"/name,report)
  assets = {row["name"]:row for row in request(endpoint+"/"+str(release["id"])+"/assets")}
  upload_url = release["upload_url"].split("{",1)[0]
  import http.client
  from urllib.parse import urlsplit,quote
  for path in sorted((folder/"release").iterdir()):
    if not path.is_file() or path.name not in {"manifest.json","precompiled.json","precompiled-runtime.tar.gz","big_driving_tinygrad.pkl","training.json","evaluation.json","closed-loop-acceptance.json","device-acceptance.json","compile.json"}:
      continue
    checksum = digest_file(path)
    if path.name in assets:
      if assets[path.name].get("digest") != "sha256:"+checksum:
        raise ValueError("remote draft asset differs; inspect without overwriting: "+path.name)
      continue
    # Stream large artifacts; never load an 800 MB model into the dashboard process.
    url = urlsplit(upload_url+"?name="+quote(path.name))
    connection = http.client.HTTPSConnection(url.netloc,timeout=600)
    try:
      connection.putrequest("POST",url.path+"?"+url.query)
      for key,value in {"Authorization":"Bearer "+token,"Content-Type":"application/octet-stream","Content-Length":str(path.stat().st_size),"User-Agent":"FormosaPilot-Training-Studio"}.items():
        connection.putheader(key,value)
      connection.endheaders()
      with path.open("rb") as stream:
        while chunk:=stream.read(1024*1024):
          connection.send(chunk)
      response = connection.getresponse()
      result = json.loads(response.read())
      if response.status!=201 or result.get("digest")!="sha256:"+checksum:
        raise ValueError("GitHub asset upload/hash verification failed: "+path.name)
    finally:
      connection.close()
  remote = request(endpoint+"/"+str(release["id"]),"PATCH",{"draft":False})
  state.update(published=True,url=remote["html_url"],manifest_url=f"https://github.com/{repository}/releases/download/{version}/manifest.json",published_at=time.time())
  write_json(folder/"release.json",state)
  store.event("版本已推送至 GitHub Release",version)
  return state


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument("command",choices=("publish","accept"))
  parser.add_argument("--root",required=True)
  parser.add_argument("--version",required=True)
  parser.add_argument("--closed-loop")
  parser.add_argument("--device")
  args=parser.parse_args()
  store=Store(args.root)
  try:
    result=accept(store,args.version,args.closed_loop,args.device) if args.command=="accept" else publish(store,args.version)
    print(json.dumps(result,ensure_ascii=False))
  except Exception as exc:
    store.event("發布／驗收失敗："+str(exc),args.version)
    raise
  finally:
    if args.command=="publish":
      (store.root/"runs"/args.version/"publish-request.json").unlink(missing_ok=True)


if __name__=="__main__":
  main()
