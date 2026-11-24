"""Device-compiled internal models from the sunnypilot model selector catalog."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import urllib.request

from openpilot.common import big_model_catalog as library
from openpilot.common.file_chunker import get_existing_chunks

# Original supercombo graphs from the commaai/openpilot revisions in sunnypilot's
# driving_models_v25.json. Compile locally for this fork's tinygrad and cameras.
MODELS = {
  'cd210': ('CD210', None),
  'mrlv2': ('Michael RL V2', '278b8ce2657011c54403459102ba742af407aafe239fff8392131977d128f842'),
  'rebel': ('Rebel Legion', '15e563da34889318e41321a2559682d417416602de9b6f5093c3be0e6766419d'),
}
SIZE = 96599486
LFS = 'https://gitlab.com/commaai/openpilot-lfs.git/info/lfs/objects/batch'
download_lock = threading.Lock()


def directory():
  return library.storage() / 'internal'


def artifact(key, suffix):
  return directory() / (MODELS[key][1] + suffix)


def pending():
  key = library.read_json(directory() / 'selection.json').get('selected')
  return key if isinstance(key, str) and key in MODELS else 'cd210'


def state():
  data = library.read_json(directory() / 'boot.json')
  return data if data.get('boot') == library.boot_id() and isinstance(data.get('active'), str) and data['active'] in MODELS else {}


def active():
  return state().get('active', 'cd210')


def verify(path, expected):
  if not path.is_file() or path.stat().st_size != SIZE:
    return False
  with path.open('rb') as stream:
    return hashlib.file_digest(stream, 'sha256').hexdigest() == expected


def select(key, offroad):
  if key not in MODELS or not offroad():
    raise ValueError('Park before selecting a model')
  with download_lock:
    folder = directory()
    folder.mkdir(parents=True, exist_ok=True)
    oid = MODELS[key][1]
    if oid and not verify(artifact(key, '.onnx'), oid):
      body = json.dumps({'operation': 'download', 'transfers': ['basic'], 'objects': [{'oid': oid, 'size': SIZE}]}).encode()
      headers = {'Accept': 'application/vnd.git-lfs+json', 'Content-Type': 'application/vnd.git-lfs+json'}
      with urllib.request.urlopen(urllib.request.Request(LFS, body, headers), timeout=30) as reply:
        obj, = json.loads(reply.read(65536))['objects']
      if obj.get('oid') != oid or obj.get('size') != SIZE:
        raise ValueError('Unexpected model manifest')
      link = obj['actions']['download']
      if not link['href'].startswith('https://'):
        raise ValueError('Invalid download URL')
      with tempfile.NamedTemporaryFile(dir=folder, delete=False) as f:
        temp = Path(f.name)
      try:
        with urllib.request.urlopen(urllib.request.Request(link['href'], headers=link.get('header', {})), timeout=35) as src, temp.open('wb') as dst:
          while chunk := src.read(1024 * 1024):
            if not offroad() or dst.tell() + len(chunk) > SIZE:
              raise ValueError('Download interrupted')
            dst.write(chunk)
        if not verify(temp, oid):
          raise ValueError('Model verification failed')
        temp.replace(artifact(key, '.onnx'))
      finally:
        temp.unlink(missing_ok=True)
    if not offroad():
      raise ValueError('Park before selecting a model')
    library.atomic_json(folder / 'selection.json', {'selected': key})


def record(key, failed=False):
  library.atomic_json(directory() / 'boot.json', {'boot': library.boot_id(), 'active': key, 'failed': failed})


def prepare_boot():
  if state():
    return
  key = pending()
  if key != 'cd210':
    try:
      if not verify(artifact(key, '.onnx'), MODELS[key][1]):
        raise ValueError('Invalid cached model')
      subprocess.run(['scons', '-j1', 'sunny_internal_model'], cwd=library.ROOT, check=True,
                     env={**os.environ, 'SUNNY_COMPILE_INTERNAL': key})
      parts = get_existing_chunks(artifact(key, '.pkl'))
      payload = parts[1:] if str(parts[0]).endswith('.chunkmanifest') else parts
      if sum(Path(part).stat().st_size for part in payload) == 0:
        raise ValueError('Empty compiled model')
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
      print(f'Internal model preparation failed: {exc}. Using CD210.', flush=True)
      record('cd210', True)
      return
  record(key)


if __name__ == '__main__':
  prepare_boot()
