"""Bounded, in-process camera diagnostics carried by existing owner-only health sync."""
import threading
import time

CAMERAS = ('wide-road', 'driver')
lock = threading.Lock()
states = {}


def update(channel, stage, error=None, sent=False):
  if channel not in (*CAMERAS, 'watch'):
    raise ValueError('invalid diagnostic channel')
  now = time.monotonic()
  with lock:
    previous = states.get(channel, {})
    value = {**previous, 'stage':stage or previous.get('stage', 'unknown'), 'updated':now, 'error':None}
    if error is not None:
      status = getattr(getattr(error, 'response', None), 'status_code', None)
      value['error'] = f'HTTP {status}' if type(status) is int and 100 <= status <= 599 else type(error).__name__[:64]
    if sent:
      value['frames'] = previous.get('frames', 0)+1
      value['last_frame'] = now
    states[channel] = value


def snapshot():
  now = time.monotonic()
  result = {'camera_diagnostics_version':1}
  with lock:
    for channel in (*CAMERAS, 'watch'):
      value = states.get(channel, {})
      fresh = 0 <= now-value.get('updated', -1000) <= 15
      prefix = 'camera_'+channel.replace('-', '_')
      result[prefix+'_state'] = value.get('stage', 'unknown') if fresh else 'unavailable'
      result[prefix+'_error'] = value.get('error') if fresh else None
      if channel in CAMERAS:
        result[prefix+'_frames'] = value.get('frames', 0)
        result[prefix+'_frame_age_s'] = round(max(0, now-value['last_frame']), 1) if 'last_frame' in value else None
  return result
