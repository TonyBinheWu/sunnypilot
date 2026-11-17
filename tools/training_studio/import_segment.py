"""Explicit owner import of existing recordings into the same verified inbox contract."""
import argparse
import hashlib
from pathlib import Path
import shutil
import time

from tools.training_studio.store import write_json
from openpilot.sunnypilot.formosalink.training_protocol import FILES, POLICY, digest_file


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument("source",type=Path)
  parser.add_argument("--inbox",type=Path,required=True)
  parser.add_argument("--route-group",required=True,help="same complete route must use the same group")
  parser.add_argument("--authorized-for-training",action="store_true",required=True)
  args=parser.parse_args()
  source=args.source.resolve()
  files=[path for path in source.iterdir() if path.name in FILES and path.is_file() and not path.is_symlink()]
  names={path.name for path in files}
  if not {"fcamera.hevc","ecamera.hevc"}<=names or not names&{"rlog","rlog.zst","rlog.bz2"}:
    raise ValueError("a closed rlog and both front camera videos are required")
  group=hashlib.sha256(args.route_group.encode()).hexdigest()
  segment=hashlib.sha256((str(source)+group).encode()).hexdigest()
  destination=args.inbox.resolve()/segment
  destination.mkdir(parents=True,exist_ok=False)
  entries=[]
  for path in files:
    output=destination/path.name
    shutil.copyfile(path,output)
    entries.append({"filename":path.name,"size":output.stat().st_size,"sha256":digest_file(output)})
  write_json(destination/"complete.json",{"version":1,"policy":POLICY,"consent_source":"explicit_operator_import",
    "received_at":time.time(),"route_group":group,"segment":segment,"files":entries})
  print(destination)


if __name__=="__main__":
  main()
