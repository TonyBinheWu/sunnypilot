"""Explicit, parked selection of an immutable Studio release; applied on the next boot."""
import argparse
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit

PUBLISHER="TonyBinheWu/sunnypilot"


def directory():
  override=os.getenv("CARROT_BIG_MODEL_DIR")
  return Path(override) if override else Path('/data/media/0/carrot/models') if Path('/TICI').is_file() else Path.home()/'.comma/models'


def validate_url(value):
  parsed=urlsplit(value)
  prefix=f'/{PUBLISHER}/releases/download/'
  if parsed.scheme!='https' or parsed.netloc!='github.com' or parsed.query or parsed.fragment or not parsed.path.startswith(prefix):
    raise ValueError('only immutable releases from the configured model publisher are supported')
  suffix=parsed.path.removeprefix(prefix)
  if not re.fullmatch(r'n16-[A-Za-z0-9-]+/manifest\.json',suffix):
    raise ValueError('invalid Studio release manifest')
  return value


def selected_url(root=None):
  try:
    data=json.loads(((Path(root) if root else directory())/'training-selection.json').read_text(encoding='utf-8'))
    return validate_url(data['manifest_url'])
  except (OSError,ValueError,KeyError,TypeError):
    return ''


def save_selection(url,root=None):
  url=validate_url(url)
  root=Path(root) if root else directory()
  root.mkdir(parents=True,exist_ok=True)
  fd,temporary=tempfile.mkstemp(prefix='.training-selection-',dir=root)
  try:
    with os.fdopen(fd,'w',encoding='utf-8') as stream:
      json.dump({'manifest_url':url,'apply':'next_boot'},stream)
      stream.flush()
      os.fsync(stream.fileno())
    os.replace(temporary,root/'training-selection.json')
  finally:
    if os.path.exists(temporary):
      os.unlink(temporary)


def main():
  parser=argparse.ArgumentParser(description=__doc__)
  commands=parser.add_subparsers(dest='command',required=True)
  commands.add_parser('manifest-url')
  commands.add_parser('restore-catalog')
  command=commands.add_parser('select')
  command.add_argument('--manifest-url',required=True)
  args=parser.parse_args()
  if args.command=='manifest-url':
    print(selected_url())
    return
  from openpilot.common.params import Params
  if not Params().get_bool('IsOffroad'):
    raise SystemExit('Park before selecting a trained model')
  if args.command=='restore-catalog':
    (directory()/'training-selection.json').unlink(missing_ok=True)
    print('Original catalog will be used on the next boot')
    return
  url=validate_url(args.manifest_url)
  from openpilot.selfdrive.modeld.big_model import deliver_model
  from openpilot.selfdrive.modeld.big_model_status import BigModelStatusReporter
  if not deliver_model(url,directory(),BigModelStatusReporter(directory())):
    raise SystemExit('Model download/runtime verification failed; selection not changed')
  save_selection(url)
  print('Model and pinned runtime downloaded and verified; selected for the next boot')


if __name__=='__main__':
  main()
