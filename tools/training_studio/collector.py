"""Private, signed, resumable synchronization of contributed datasets from FormosaLink."""
import argparse
import json
import os
import time
from pathlib import Path
import urllib.request

from tools.training_studio.store import Store, read_json, write_json
from openpilot.sunnypilot.formosalink.identity import create, read
from openpilot.sunnypilot.formosalink.protocol import canonical, public_key_text, sign
from openpilot.sunnypilot.formosalink.training_protocol import FILES, POLICY, digest_file, valid_hash


def sync(store,stop=None):
  config=store.config()["collector"]
  identity,private,_=read(config["identity_directory"])
  origin=identity["origin"]
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  def request(operation,**fields):
    body=canonical(sign(private,identity["device_id"],"training-worker",{"operation":operation,**fields}))
    return opener.open(urllib.request.Request(origin+"/api/v1/training-worker",data=body,
      headers={"Content-Type":"application/json","User-Agent":"FormosaPilot-Training-Studio/1"}),timeout=60)
  cursor=read_json(store.root/"collector-cursor.json",{"cursor":0})["cursor"]
  with request("index",cursor=cursor) as response:
    raw=response.read(1024*1024)
    page=json.loads(raw)
  write_json(store.root/"collection.json",{**page.get("summary",{}),"updated":time.time(),"connected":True})
  inbox=store.root/"inbox"
  inbox.mkdir(exist_ok=True)
  for row in page["datasets"]:
    if stop is not None and (stop.is_set() or not store.enabled()):
      raise InterruptedError("dataset synchronization paused")
    manifest=row["manifest"]
    if not valid_hash(row["id"]) or manifest.get("policy")!=POLICY or not valid_hash(manifest.get("route_group")):
      raise ValueError("invalid contributed dataset manifest")
    folder=inbox/row["id"]
    folder.mkdir(exist_ok=True)
    for entry in manifest["files"]:
      if entry["filename"] not in FILES or not valid_hash(entry["sha256"]):
        raise ValueError("unsupported contributed file")
      path=folder/entry["filename"]
      if path.is_file() and path.stat().st_size==entry["size"] and digest_file(path)==entry["sha256"]:
        continue
      part=path.with_suffix(path.suffix+".part")
      offset=part.stat().st_size if part.is_file() else 0
      if offset>entry["size"]:
        raise ValueError("local partial download is oversized")
      with part.open("ab") as stream:
        while offset<entry["size"]:
          if stop is not None and (stop.is_set() or not store.enabled()):
            raise InterruptedError("dataset synchronization paused")
          with request("file",dataset=row["id"],filename=entry["filename"],offset=offset) as response:
            if response.headers.get("X-File-SHA256")!=entry["sha256"] or response.headers.get("X-Chunk-Offset")!=str(offset):
              raise ValueError("training download identity changed")
            chunk=response.read(1024*1024+1)
          if not chunk or len(chunk)>1024*1024 or offset+len(chunk)>entry["size"]:
            raise ValueError("invalid training download chunk")
          stream.write(chunk)
          stream.flush()
          os.fsync(stream.fileno())
          offset+=len(chunk)
          write_json(store.root/"collector-progress.json",{"dataset":row["id"],"filename":entry["filename"],"bytes":offset,"total":entry["size"]})
      if digest_file(part)!=entry["sha256"]:
        part.unlink()
        raise ValueError("contributed file hash mismatch")
      os.replace(part,path)
    write_json(folder/"complete.json",manifest)
    write_json(store.root/"collector-cursor.json",{"cursor":row["seq"]})
    store.event("已同步完整授權行車片段 "+row["id"][:12])


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument("command",choices=("register-key","sync"))
  parser.add_argument("--root",required=True)
  parser.add_argument("--origin")
  args=parser.parse_args()
  store=Store(args.root)
  if args.command=="register-key":
    directory=store.root/"collector-identity"
    if not (directory/"identity.json").is_file():
      identity,private,_=create(directory,args.origin)
    else:
      identity,private,_=read(directory)
      if args.origin and identity["origin"]!=args.origin:
        raise ValueError("collector identity belongs to another origin")
    config=store.config()
    config["collector"]={"identity_directory":str(directory)}
    inbox=str(store.root/"inbox")
    config["inboxes"]=list(dict.fromkeys([*config.get("inboxes",[]),inbox]))
    write_json(store.root/"config.json",config)
    print(json.dumps({identity["device_id"]:public_key_text(private)}))
  else:
    sync(store)


if __name__=="__main__":
  main()
