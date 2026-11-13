"""Short-lived, process-owned camera demand for parked Carrot Vision viewers."""
import json
import math
import os
from pathlib import Path
import tempfile
import time

TTL = 5.0


def clock():
  return time.clock_gettime(time.CLOCK_BOOTTIME) if hasattr(time, 'CLOCK_BOOTTIME') else time.monotonic()


def lease_path():
  return Path(os.getenv('CARROT_VISION_CAMERA_LEASE', '/dev/shm/carrot-vision-camera.json'))


def camera_requested():
  try:
    path = lease_path()
    if path.is_symlink() or path.stat().st_size > 256:
      return False
    deadline = json.loads(path.read_text())['until']
    if type(deadline) not in (int, float) or not math.isfinite(deadline):
      return False
    return 0 < deadline - clock() <= TTL
  except (OSError, ValueError, TypeError, KeyError):
    return False


def enabled_camera_requested(params):
  return params.get_bool('CarrotVisionEnabled') and camera_requested()


def update_camera_request(active):
  path = lease_path()
  if not active:
    path.unlink(missing_ok=True)
    return
  name = None
  try:
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
      name = stream.name
      json.dump({'until': clock() + TTL}, stream)
    os.replace(name, path)
  finally:
    if name:
      Path(name).unlink(missing_ok=True)
