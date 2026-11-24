"""Immutable sunnypilot selector snapshot and offroad installation for both accelerators."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import urllib.request
import zipfile
from functools import lru_cache

from openpilot.common import big_model_catalog as library

AUX_STATUS = Path('/dev/shm/sunnypilot-aux-status.json')
# Plain kernels retain their build metadata. The loader uses the tinygrad submodule
# paired with sunnypilot modeld_v2 at abada631, which reads both catalog generations.
RUNTIME_REF = '92b742f711c7d216fd3ed7a46a30a959e3c43bd4'
RUNTIME_SHA = 'b51c8befd2a9ee06e9e500531ef99da379c7f4b368f406d7d44e2e05e6efd7e6'
WARPS = {
  'driving_warp_1344x760_tinygrad.pkl': ('d776c72125156b5dd3eb59768409401e28c8a52a3a619cd3b9f02c10a156fda6', 3699072),
  'driving_warp_1928x1208_tinygrad.pkl': ('a3f13ed12e087817a86afd48b2496c66c4f61a1925065b676b2945e81fabaacd', 7924864),
  'big_driving_warp_1344x760_tinygrad.pkl': ('f1689356ff8e516f87e3d75f6b53e66953a11ee5a97e859b4808c9a16bfe671b', 3677806),
  'big_driving_warp_1928x1208_tinygrad.pkl': ('56cc9690e0e9fb719323d2c6646c1305e8bc6bbdfdc807724a605a0d0a37554b', 7904366),
}


@lru_cache(maxsize=1)
def catalog():
  return json.loads((library.DIRECTORY / 'sunnypilot.json').read_bytes())


def directory():
  return library.storage() / 'sunnypilot'


def warp_directory():
  return directory() / 'warps'


def model_file(key):
  return directory() / (catalog()[key]['sha256'] + '.pkl')


def runtime():
  return directory() / RUNTIME_REF


def digest(path):
  with path.open('rb') as f:
    return hashlib.file_digest(f, 'sha256').hexdigest()


def download(url, sha, path, offroad, limit):
  if path.is_file() and digest(path) == sha:
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
    temp = Path(f.name)
  try:
    with urllib.request.urlopen(url, timeout=45) as src, temp.open('wb') as dst:
      hasher = hashlib.sha256()
      while block := src.read(1 << 20):
        if not offroad() or dst.tell() + len(block) > limit:
          raise ValueError('Model download interrupted')
        dst.write(block)
        hasher.update(block)
    if hasher.hexdigest() != sha or not offroad():
      raise ValueError('Model verification failed')
    temp.replace(path)
  finally:
    temp.unlink(missing_ok=True)


def install_runtime(offroad):
  target = runtime()
  if (target / 'tinygrad/__init__.py').is_file():
    return
  ref, sha = RUNTIME_REF, RUNTIME_SHA
  archive = directory() / (ref + '.zip')
  download('https://codeload.github.com/sunnypilot/tinygrad/zip/' + ref, sha, archive, offroad, 25 << 20)
  prefix = f'tinygrad-{ref}/'
  with tempfile.TemporaryDirectory(dir=directory()) as tmp:
    dest = Path(tmp) / 'runtime'
    with zipfile.ZipFile(archive) as z:
      for info in z.infolist():
        if info.is_dir() or not info.filename.startswith(prefix + 'tinygrad/'):
          continue
        if not offroad():
          raise ValueError('Installation interrupted')
        out = dest / info.filename.removeprefix(prefix)
        if not out.resolve().is_relative_to(dest.resolve()):
          raise ValueError('Invalid runtime path')
        out.parent.mkdir(exist_ok=True, parents=True)
        with z.open(info) as src, out.open('wb') as dst:
          shutil.copyfileobj(src, dst)
    if not (dest / 'tinygrad/__init__.py').is_file():
      raise ValueError('Missing tinygrad runtime')
    try:
      dest.rename(target)
    except OSError:
      if not (target / 'tinygrad/__init__.py').is_file():
        raise


def prefs(boot=False):
  value = library.read_json(directory() / ('boot.json' if boot else 'selection.json'))
  if boot and value.get('boot') != library.boot_id():
    return {}
  return value


def key_for(big, boot=False):
  key = prefs(boot).get('big' if big else 'small')
  return key if isinstance(key, str) and catalog().get(key, {}).get('big') is big else None


def save(field, value):
  with library.library_lock():
    library.atomic_json(directory() / 'selection.json', {**prefs(), field: value})


def warp_url(sha, size):
  body = json.dumps({'operation': 'download', 'transfers': ['basic'], 'objects': [{'oid': sha, 'size': size}]}).encode()
  request = urllib.request.Request('https://huggingface.co/sunnypilot/sunnypilot-lfs.git/info/lfs/objects/batch', data=body,
                                   headers={'Content-Type': 'application/vnd.git-lfs+json', 'Accept': 'application/vnd.git-lfs+json'})
  with urllib.request.urlopen(request, timeout=30) as resp:
    obj, = json.loads(resp.read(65536))['objects']
  href = obj['actions']['download']['href']
  if obj['oid'] != sha or obj['size'] != size or not href.startswith('https://'):
    raise ValueError('Unexpected camera warp manifest')
  return href


def select(big, key, offroad):
  entry = catalog()[key]
  if entry['big'] != big or not offroad():
    raise ValueError('Park before selecting a model')
  install_runtime(offroad)
  for name, (sha, size) in WARPS.items():
    if name.startswith('big_') == big:
      path = warp_directory() / name
      if not path.is_file() or digest(path) != sha:
        download(warp_url(sha, size), sha, path, offroad, size)
  download(entry['url'], entry['sha256'], model_file(key), offroad, 3 << 30)
  if not offroad():
    raise ValueError('Park before selecting a model')
  save('big' if big else 'small', key)


def freeze_boot():
  with library.library_lock():
    if prefs(True).get('boot') != library.boot_id():
      library.atomic_json(directory() / 'boot.json', {**prefs(), 'boot': library.boot_id()})


def auxiliary_map_demand(now):
  status = library.read_json(AUX_STATUS)
  eof = status.get('eof')
  return status.get('nav') is True and isinstance(eof, (float,int)) and 0 <= now-eof < 2.


def failed_key(big):
  state = library.read_json(directory() / 'load-status.json')
  return state.get(str(big)) if state.get('boot') == library.boot_id() else None


def mark_load(big, failed):
  try:
    with library.library_lock():
      path = directory() / 'load-status.json'
      state = library.read_json(path)
      if state.get('boot') != library.boot_id():
        state = {'boot': library.boot_id()}
      library.atomic_json(path, {**state, str(big): failed})
  except OSError:
    pass


if __name__ == '__main__':
  freeze_boot()
