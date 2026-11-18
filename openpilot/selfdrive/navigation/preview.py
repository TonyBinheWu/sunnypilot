"""One small tmpfs image shared by Web and USB display (never model input)."""
import os
import json
import math
from pathlib import Path
import time

PREVIEW_PATH = Path('/dev/shm/carrot_nav_map.png')
PREVIEW_MAX_AGE = 2.
WEB_DEMAND_PATH = Path('/dev/shm/carrot_nav_web')
STATUS_PATH = Path('/dev/shm/carrot_nav_status.json')
VIEW_PATH = Path('/dev/shm/carrot_nav_view.json')


def write_navigation_view(route, gps, route_id, *, instruction=None, path=VIEW_PATH, now=None):
  """Read-only UI copy of the exact active navRoute, never a model input.

  Keep it in tmpfs; no Google imagery/content enters mapsd or the model.
  Called at most once a second, independently of tile availability.
  """
  now = time.time() if now is None else now
  position = None if gps is None else {'lat': gps.latitude, 'lng': gps.longitude}
  payload = {'generated_at': now, 'route_id': int(route_id), 'position': position,
             'coordinates': [[float(lon), float(lat)] for lon, lat in route] if route_id else []}
  payload['instruction'] = None
  if route_id and instruction is not None:
    distances = [float(getattr(instruction, key)) for key in ('maneuverDistance', 'distanceRemaining', 'timeRemaining')]
    if all(math.isfinite(value) and 0 <= value <= 1e8 for value in distances):
      payload['instruction'] = dict(zip(('distance', 'remaining_m', 'remaining_s'), distances))
      payload['instruction'].update(text=str(instruction.maneuverPrimaryText)[:256], modifier=str(instruction.maneuverModifier)[:40])
  temporary = path.with_suffix('.tmp')
  temporary.write_text(json.dumps(payload, allow_nan=False, separators=(',', ':')), encoding='utf-8')
  os.replace(temporary, path)


def preview_fresh(path=PREVIEW_PATH):
  try:
    return 0 <= time.time() - path.stat().st_mtime < PREVIEW_MAX_AGE  # noqa: TID251 - filesystem mtime is wall clock
  except OSError:
    return False


def write_preview(image, path=PREVIEW_PATH, *, reason='ready'):
  from PIL import Image
  temporary = path.with_suffix('.tmp')
  Image.fromarray(image).save(temporary, format='PNG', compress_level=1)
  os.replace(temporary, path)
  status = path.with_name(STATUS_PATH.name)
  temporary = status.with_suffix('.tmp')
  temporary.write_text(json.dumps({'reason': reason}), encoding='utf-8')
  os.replace(temporary, status)


def preview_reason():
  try:
    return str(json.loads(STATUS_PATH.read_text(encoding='utf-8'))['reason'])
  except (OSError, ValueError, KeyError):
    return 'waiting'
