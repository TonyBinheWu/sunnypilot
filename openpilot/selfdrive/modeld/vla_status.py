"""Local C4 VLA observation status. Age is always measured from camera exposure."""
import json
from pathlib import Path
import time

from openpilot.tools.vla.replay import ARTIFACTS, REVISION

WEIGHTS = Path('/data/vla-weights')
STATUS = Path('/dev/shm/carrot_vla_observation.json')
TTL_NS = 500_000_000


def camera_clock():
  return time.clock_gettime_ns(time.CLOCK_BOOTTIME) if hasattr(time, 'CLOCK_BOOTTIME') else time.monotonic_ns()


def parked(params):
  return params is not None and params.get_bool('IsOffroad') and not any(
    params.get_bool(k) for k in ('IsOnroad', 'IsEngaged', 'ForceOffroad', 'ForceOffroadActive'))


def prepare_weights(offroad, directory=WEIGHTS):
  from openpilot.common.sunny_models import download
  import shutil
  directory.mkdir(parents=True, exist_ok=True)
  for name, (size, sha) in ARTIFACTS.items():
    path = directory / name
    if not offroad():
      raise ValueError('Park before preparing VLA weights')
    if not path.exists() and shutil.disk_usage(directory).free < size + (2 << 30):
      raise OSError('Insufficient free space for VLA weights')
    url = f'https://huggingface.co/mradermacher/PhysicalAI-reason-VLA-GGUF/resolve/{REVISION}/{name}'
    download(url, sha, path, offroad, size)


def write_status(state, **fields):
  tmp = STATUS.with_suffix('.tmp')
  tmp.write_text(json.dumps(dict(state=state, updated=camera_clock(), **fields), allow_nan=False))
  tmp.replace(STATUS)


def read_status(now=None, path=STATUS):
  try:
    with path.open('rb') as f:
      row = json.loads(f.read(4096))
    now = camera_clock() if now is None else now
    updated = row.pop('updated')
    if updated > now:
      return {'state': 'idle'}
    summary = {'session': row['session']} if isinstance(row.get('session'), dict) else {}
    if now - updated >= 3_000_000_000:
      if row.get('state') in ('too_slow', 'usb_unavailable', 'worker_failed', 'primary_guard', 'primary_owns_gpu'):
        return {'state': 'idle', 'last_error': row['state'], **summary}
      return {'state': 'idle', **summary}
    if row['state'] == 'result' and not 0 <= now - row['eof'] < TTL_NS:
      return {'state': 'expired', **summary}
    return row
  except (OSError, ValueError, KeyError, TypeError, AttributeError):
    return {'state': 'idle'}


def compare(primary, action):
  # Curvature alone cannot distinguish a turn at a junction from an ordinary road bend.
  # Only an explicit primary stop decision has a directly comparable VLA label.
  if action['longitudinal'] == 'stop':
    return 'both_stop' if primary['should_stop'] else 'only_vla_stop'
  if primary['should_stop'] and action['longitudinal'] in ('cruise', 'pass'):
    return 'only_primary_stop'
  return 'inconclusive'
