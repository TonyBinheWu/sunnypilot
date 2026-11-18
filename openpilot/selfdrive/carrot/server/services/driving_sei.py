"""Bounded, read-only SEI index for the same video served by the log player."""
import asyncio
from collections import OrderedDict
import json
import math
import os
import shutil
import subprocess
import tempfile
import threading

from aiohttp import web
from pathlib import Path
from openpilot.system.loggerd.driving_metadata import metadata_from_nals

MAX_VIDEO_BYTES = 8 * 1024 * 1024
MAX_PROBE_BYTES = 26 * 1024 * 1024
MAX_SAMPLES = 6000
NATIVE_READER = Path(__file__).resolve().parents[4] / 'system/loggerd/sei_reader'
_cache = OrderedDict()
_lock = threading.Lock()
FIELDS = ('speed_mps', 'steering_angle_deg', 'gas', 'brake', 'gas_pressed', 'brake_pressed',
          'control_enabled', 'lateral_active', 'longitudinal_active', 'cruise_enabled')



def _number(value, low, high):
  return value if type(value) in (int, float) and math.isfinite(value) and low <= value <= high else None


def _sample(item, pts):
  car_time, control_time, frame_time = (item.get(k) for k in ('car_mono_ns', 'control_mono_ns', 'frame_mono_ns'))
  def fresh(t):
    return type(t) is int and type(frame_time) is int and 0 <= frame_time - t <= 250000000
  row = {'time_s': pts, 'frame_id': item.get('frame_id') if type(item.get('frame_id')) is int else None}
  bounds = {'speed_mps': (0, 150), 'steering_angle_deg': (-3000, 3000), 'gas': (0, 1), 'brake': (0, 1)}
  for key in FIELDS:
    valid = fresh(control_time if key in ('control_enabled', 'lateral_active', 'longitudinal_active') else car_time)
    value = item.get(key)
    row[key] = (_number(value, *bounds[key]) if key in bounds else value if type(value) is bool else None) if valid else None
  return row


def timeline_from_native(raw):
  samples=[]
  for line in raw.decode('ascii').splitlines():
    parts=line.split('\t')
    if len(parts)!=3 or parts[1] not in ('h264','hevc'):
      continue
    pts=float(parts[0])
    if not math.isfinite(pts) or not 0 <= pts <= 3600 or len(parts[2])>16384:
      continue
    for item in metadata_from_nals([bytes.fromhex(parts[2])],parts[1]):
      samples.append(_sample(item,pts))
      if len(samples)>MAX_SAMPLES:
        return {'status':'too_large','samples':[]}
  samples.sort(key=lambda row:row['time_s'])
  return {'status':'ready' if samples else 'no_sei','samples':samples}


def load_sei(segment):
  from ..features.dashcam.catalog import source_video
  from ..features.dashcam.paths import segment_dir
  # One metadata job at a time; no video decoding, control IPC or rlog scan.
  with _lock:
    path, _ = source_video(segment_dir(segment))
    stat = os.stat(path)
    key = (path, stat.st_size, stat.st_mtime_ns)
    if key in _cache:
      _cache.move_to_end(key)
      return _cache[key]
    if stat.st_size > MAX_VIDEO_BYTES:
      return {'status': 'too_large', 'samples': []}
    executable = NATIVE_READER
    if not executable.is_file():
      return {'status':'unavailable','samples':[]}
    command=[str(executable),path]
    if os.name=='posix' and shutil.which('nice'):
      command=[shutil.which('nice'),'-n','15',*command]
    with tempfile.TemporaryFile() as output:
      result=subprocess.run(command,stdout=output,stderr=subprocess.DEVNULL,timeout=20,check=False)
      if result.returncode or output.tell()>MAX_PROBE_BYTES:
        return {'status':'unavailable','samples':[]}
      output.seek(0)
      data=timeline_from_native(output.read(MAX_PROBE_BYTES+1))
    _cache[key] = data
    while len(_cache) > 2:
      _cache.popitem(last=False)
    return data


async def api_dashcam_sei(request):
  # Admit before scheduling so abandoned browser requests cannot grow a queue.
  task = request.app.get('dashcam_sei_task')
  segment = request.match_info.get('segment', '')
  if task is not None and not task.done():
    if request.app.get('dashcam_sei_segment') != segment:
      return web.json_response({'ok': True, 'status': 'busy', 'samples': []}, headers={'Cache-Control': 'no-store'})
  else:
    task = asyncio.create_task(asyncio.to_thread(load_sei, segment))
    # A disconnected viewer must not leave an unobserved worker exception.
    task.add_done_callback(lambda finished: None if finished.cancelled() else finished.exception())
    request.app['dashcam_sei_task'] = task
    request.app['dashcam_sei_segment'] = segment
  try:
    return web.json_response({'ok': True, **await asyncio.shield(task)}, headers={'Cache-Control': 'no-store'})
  except web.HTTPException:
    raise
  except (OSError, ValueError, subprocess.SubprocessError):
    return web.json_response({'ok': True, 'status': 'unavailable', 'samples': []}, headers={'Cache-Control': 'no-store'})
