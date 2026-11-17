"""Stage only Training Studio changes into the existing IIS package, preserving Carrot features."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from tools.training_studio.integrate import NEW_FILES


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--checkout',type=Path,required=True)
  parser.add_argument('--website',type=Path,required=True)
  parser.add_argument('--worker-registration',type=Path,required=True)
  parser.add_argument('--write',action='store_true')
  args=parser.parse_args()
  checkout=args.checkout.resolve()
  website=args.website.resolve()
  package=website/'App_Data/server-package'
  if not (package/'formosalink/server/app.py').is_file():
    raise ValueError('existing managed FormosaLink package required')
  mapping={}
  for name in NEW_FILES:
    target=website/Path(name).name if name.startswith('formosalink/web/') else package/name
    mapping[target]=checkout/name
  for name,target in (('formosalink/server/app.py',package/'formosalink/server/app.py'),('formosalink/web/app.js',website/'app.js')):
    before=subprocess.check_output(['git','show','HEAD:'+name],cwd=checkout).decode('utf-8').replace('\r\n','\n')
    current=target.read_text(encoding='utf-8').replace('\r\n','\n')
    candidate=(checkout/name).read_text(encoding='utf-8').replace('\r\n','\n')
    if current not in (before,candidate):
      raise ValueError('production source changed independently; refusing to overwrite '+name)
    mapping[target]=checkout/name
  source=Path(__file__).resolve().parents[2]
  mapping[website/'App_Data/enable-training.ps1']=source/'tools/training_studio/enable-training.ps1'
  mapping[website/'App_Data/training-worker-registration.json']=args.worker_registration.resolve()
  mapping[website/'App_Data/docs/TRAINING_STUDIO.md']=source/'tools/training_studio/README.md'
  backup=source/'build/training-studio-iis-backup'/time.strftime('%Y%m%dT%H%M%S')
  records=[]
  for target,original in mapping.items():
    if not original.is_file():
      raise ValueError('missing deployment source: '+str(original))
    if not target.resolve().is_relative_to(website):
      raise ValueError('deployment path escaped website')
    if args.write:
      if target.is_file():
        saved=backup/target.relative_to(website)
        saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(target,saved)
      target.parent.mkdir(parents=True,exist_ok=True)
      shutil.copyfile(original,target)
      if hashlib.sha256(original.read_bytes()).digest()!=hashlib.sha256(target.read_bytes()).digest():
        raise ValueError('deployment hash mismatch')
    records.append(str(target.relative_to(website)))
  print(json.dumps({'staged':args.write,'files':records,'backend_restart_required':True,'backup':str(backup)},ensure_ascii=False))


if __name__=='__main__':
  main()
