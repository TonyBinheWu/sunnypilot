"""Immutable sunnypilot selector snapshot and offroad installation for both accelerators."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import urllib.request
import uuid
import zipfile
from functools import lru_cache

from openpilot.common import big_model_catalog as library
from openpilot.common.model_download import copy_download, notify

# Plain kernels retain their build metadata. The loader uses the tinygrad submodule
# paired with sunnypilot modeld_v2 at abada631, which reads both catalog generations.
LAT2V = 'lat2v'
LAT2V_NAME = 'lat2v (Nvidia)'
LAT2V_PARK_MESSAGES = {
  'forced_offroad': 'Forced offroad is active. Turn the ignition off.',
  'engaged': 'Disengage assistance and turn the ignition off.',
  'offroad': 'Wait for ignition-off offroad mode.',
}

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


def download(url, sha, path, offroad, limit, progress=None, name=None, size=None):
  name = name or path.name
  if path.is_file():
    notify(progress, 'verifying', name)
    if digest(path) == sha:
      return
  path.parent.mkdir(parents=True, exist_ok=True)
  with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
    temp = Path(f.name)
  try:
    notify(progress, 'connecting', name)
    with urllib.request.urlopen(url, timeout=45) as src, temp.open('wb') as dst:
      actual = copy_download(src, dst, offroad, limit, name, progress, size)
    if actual != sha or not offroad():
      raise ValueError('Model verification failed')
    temp.replace(path)
  finally:
    temp.unlink(missing_ok=True)


def install_runtime(offroad, progress=None):
  target = runtime()
  if (target / 'tinygrad/__init__.py').is_file():
    return
  ref, sha = RUNTIME_REF, RUNTIME_SHA
  archive = directory() / (ref + '.zip')
  download('https://codeload.github.com/sunnypilot/tinygrad/zip/' + ref, sha, archive, offroad, 25 << 20, progress, 'tinygrad.zip')
  notify(progress, 'installing', 'tinygrad')
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
  if big and key == LAT2V:
    return key
  return key if isinstance(key, str) and catalog().get(key, {}).get('big') is big else None


def save(field, value):
  with library.library_lock():
    library.atomic_json(directory() / 'selection.json', {**prefs(), field: value})


def lat2v_supported():
  try:
    from openpilot.system.hardware import HARDWARE
    return HARDWARE.get_device_type() == 'mici'
  except (ImportError, OSError):
    return False


def lat2v_request(selection=None):
  request = (prefs() if selection is None else selection).get('lat2v_install')
  if isinstance(request, dict) and isinstance(request.get('id'), str) and request.get('state') in (
      'queued', 'preparing', 'waiting_egpu', 'retry_download', 'failed'):
    return request
  return {}


def lat2v_install_status(park_block):
  request = lat2v_request()
  if not request:
    return {}
  state = request['state']
  if park_block and state in ('queued', 'preparing', 'retry_download'):
    return {'state': 'waiting_offroad'}
  if state != 'preparing':
    return {k: request[k] for k in ('state', 'detail') if k in request}
  from openpilot.selfdrive.alpamayo.install import STATUS
  progress = library.read_json(STATUS)
  if not progress or progress.get('time', 0) < request.get('since', 0):
    return {'state': state}
  return {'state': 'verifying_gpu' if progress.get('step') == 'verify' else state,
          'progress': {'phase': progress.get('phase', 'installing'), 'file': progress.get('text', ''),
                       'received': progress.get('received', 0), 'total': progress.get('total')}}


def queue_lat2v():
  with library.library_lock():
    selection = prefs()
    request = lat2v_request(selection)
    if not request or request['state'] == 'failed':
      request = {'id': uuid.uuid4().hex, 'state': 'queued'}
      library.atomic_json(directory() / 'selection.json', {**selection, 'lat2v_install': request})
    return request


def cancel_lat2v_request():
  with library.library_lock():
    selection = prefs()
    if selection.pop('lat2v_install', None) is not None:
      library.atomic_json(directory() / 'selection.json', selection)


def update_lat2v_request(request_id, state, detail='', *, verified=None):
  """Publish progress or commit the qualified next-boot model only for the current choice."""
  with library.library_lock():
    selection = prefs()
    current = lat2v_request(selection)
    if not current or current['id'] != request_id:
      return False
    if state == 'saved':
      if verified is None or not verified():
        return False
      selection.pop('lat2v_install')
      selection['big'] = LAT2V
    else:
      request = {'id': request_id, 'state': state}
      if detail:
        request['detail'] = detail
      if state == 'preparing':
        request['since'] = time.time()
      elif request == current:
        return True
      selection['lat2v_install'] = request
    library.atomic_json(directory() / 'selection.json', selection)
    return True


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


def select(big, key, offroad, progress=None):
  entry = catalog()[key]
  if entry['big'] != big or not offroad():
    raise ValueError('Park before selecting a model')
  install_runtime(offroad, progress)
  for name, (sha, size) in WARPS.items():
    if name.startswith('big_') == big:
      path = warp_directory() / name
      notify(progress, 'verifying', name)
      if not path.is_file() or digest(path) != sha:
        notify(progress, 'connecting', name)
        download(warp_url(sha, size), sha, path, offroad, size, progress, name, size)
  download(entry['url'], entry['sha256'], model_file(key), offroad, 3 << 30, progress, entry['name'])
  if not offroad():
    raise ValueError('Park before selecting a model')
  save('big' if big else 'small', key)


_choice_lock = threading.Lock()


@contextmanager
def choice_lock():
  """Admit one model change across native UI and web processes, without queuing a stale choice."""
  if not _choice_lock.acquire(blocking=False):
    raise BlockingIOError('Another model selection is in progress')
  try:
    directory().mkdir(parents=True, exist_ok=True)
    with (directory() / '.choice.lock').open('a') as handle:
      if os.name == 'posix':
        import fcntl
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
      yield
  finally:
    _choice_lock.release()


def model_items():
  from openpilot.common import internal_models as internal
  return ([(False, key, model[0]) for key, model in internal.MODELS.items()]
          + [(True, key, model['name']) for key, model in library.available().items()]
          + [(True, LAT2V, LAT2V_NAME)]
          + [(row['big'], key, row['name']) for key, row in reversed(catalog().items())])


class Lat2vParkedError(ValueError):
  def __init__(self, reason):
    self.reason = reason
    super().__init__(LAT2V_PARK_MESSAGES[reason])


def lat2v_park_block(params):
  from openpilot.selfdrive.alpamayo.carrot import strictly_parked
  try:
    if params is not None:
      if strictly_parked(params):
        return None
      if params.get_bool('ForceOffroad') or params.get_bool('ForceOffroadActive'):
        return 'forced_offroad'
      if params.get_bool('IsEngaged'):
        return 'engaged'
  except OSError:
    pass
  return 'offroad'


def lat2v_install_requested(started, params, _CP):
  if started:
    return False
  request = lat2v_request()
  return bool(request and request['state'] != 'failed' and lat2v_supported() and lat2v_park_block(params) is None)


def choose_model(big, key, offroad, progress=None, *, params=None):
  from openpilot.common import internal_models as internal
  with choice_lock():
    if key == LAT2V:
      if not big:
        raise ValueError('lat2v requires the external GPU')
      if not lat2v_supported():
        raise ValueError('lat2v requires a comma four')
      if params is None:
        from openpilot.common.params import Params
        params = Params()
      if not offroad() or not params.get_bool('IsOffroad') or params.get_bool('IsOnroad') or params.get_bool('IsEngaged'):
        raise Lat2vParkedError(lat2v_park_block(params) or 'offroad')
      return queue_lat2v()
    if not offroad():
      raise ValueError('Park before selecting a model')
    if big and (catalog().get(key, {}).get('big') is True or key in library.available()):
      cancel_lat2v_request()
    if key in catalog():
      select(big, key, offroad, progress)
    else:
      if big:
        library.select(key)
      else:
        internal.select(key, offroad, progress)
      save('big' if big else 'small', None)


def set_primary(role, offroad):
  with choice_lock():
    if role not in ('auto', 'internal') or not offroad():
      raise ValueError('Invalid primary model selection')
    save('primary', role)


def freeze_boot():
  with library.library_lock():
    if prefs(True).get('boot') != library.boot_id():
      selection = prefs()
      selection.pop('lat2v_install', None)
      library.atomic_json(directory() / 'boot.json', {**selection, 'boot': library.boot_id()})


def internal_primary(boot=False):
  selection = prefs(boot)
  # The retired second-driving-model mode ran the selected small model as primary.
  return selection.get('primary', 'internal' if selection.get('assistant') is True else 'auto') == 'internal'


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
