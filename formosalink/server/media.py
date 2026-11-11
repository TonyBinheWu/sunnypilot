"""Single-worker, bounded, ephemeral media relay; ownership is checked per request."""
import threading
import time

from openpilot.sunnypilot.formosalink.media_protocol import MEDIA_TTL


class MediaRelay:
  def __init__(self, capacity=32, clock=time.monotonic):
    self.frames = {}
    self.lock = threading.Lock()
    self.capacity, self.clock = capacity, clock

  def _expire(self):
    now = self.clock()
    self.frames = {key: item for key,item in self.frames.items() if now <= item[0]}

  def put(self, device, frame):
    with self.lock:
      self._expire()
      previous = self.frames.get(device)
      if previous:
        old = previous[1]
        if frame['sampled_at'] < old['sampled_at'] or frame['stream'] == old['stream'] and frame['sequence'] <= old['sequence']:
          raise ValueError('old media frame')
      if device not in self.frames and len(self.frames) >= self.capacity:
        raise ValueError('media relay full')
      remaining = max(0, MEDIA_TTL - max(0, time.time() - frame['sampled_at']))
      self.frames[device] = self.clock() + remaining, frame

  def get(self, device, after):
    with self.lock:
      self._expire()
      item = self.frames.get(device)
      if not item:
        return {'available':False, 'frame':None, 'transport':'https-jpeg-preview-v1'}
      frame = item[1]
      cursor = frame['stream'] + ':' + str(frame['sequence'])
      return {'available':True, 'frame':None if after == cursor else frame, 'cursor':cursor, 'transport':'https-jpeg-preview-v1'}


def register(app, store, owner, rate):
  from fastapi import Request, HTTPException
  from cryptography.exceptions import InvalidSignature
  from openpilot.sunnypilot.formosalink.protocol import verify
  from openpilot.sunnypilot.formosalink.media_protocol import validate_frame
  relay = MediaRelay()
  app.state.media = relay

  @app.post('/api/v1/agent/media')
  async def publish(request: Request):
    rate(request,'media-publish',900)
    try:
      envelope = await request.json()
      row = store.get(envelope['device_id'])
      if not row or row['state'] != 'paired':
        raise ValueError('device unavailable')
      verified = verify(envelope, row['public_key'], 'media')
      frame = validate_frame(verified['payload'])
      store.consume_nonce(row['id'], verified['nonce'])
      relay.put(row['id'], frame)
      return {'accepted':True, 'sequence':frame['sequence']}
    except (ValueError, KeyError, TypeError, AttributeError, OverflowError, InvalidSignature) as exc:
      raise HTTPException(403,'invalid media frame') from exc

  @app.get('/api/v1/devices/{device_id}/media')
  def preview(device_id: str, request: Request, after: str = ''):
    user = owner(request)
    row = store.get(device_id)
    if not row or row['state'] != 'paired' or row['owner_id'] != user['id']:
      raise HTTPException(404,'device not found')
    if len(after) > 80:
      raise HTTPException(400,'invalid media cursor')
    rate(request,'media-view',600)
    return relay.get(device_id, after)
