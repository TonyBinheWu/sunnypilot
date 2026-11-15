"""Single-worker, bounded, ephemeral media relay; ownership is checked per request."""
import threading
import time

from openpilot.sunnypilot.formosalink.media_protocol import MEDIA_TTL


class MediaRelay:
  def __init__(self, capacity=32, clock=time.monotonic):
    self.frames = {}
    self.leases = {}
    self.lock = threading.Lock()
    self.capacity, self.clock = capacity, clock

  def _expire(self):
    now = self.clock()
    self.frames = {key: item for key,item in self.frames.items() if now <= item[0]}

  def put(self, device, frame):
    with self.lock:
      self._expire()
      device = (device, frame["source"] if frame["source"] in ("wide-road", "driver") else "road-preview")
      previous = self.frames.get(device)
      if previous:
        old = previous[1]
        if frame['sampled_at'] < old['sampled_at'] or frame['stream'] == old['stream'] and frame['sequence'] <= old['sequence']:
          raise ValueError('old media frame')
      if device not in self.frames and len(self.frames) >= self.capacity:
        raise ValueError('media relay full')
      remaining = max(0, MEDIA_TTL - max(0, time.time() - frame['sampled_at']))
      self.frames[device] = self.clock() + remaining, frame

  def get(self, device, after, camera="road-preview"):
    with self.lock:
      self._expire()
      item = self.frames.get((device, camera))
      if not item:
        return {'available':False, 'frame':None, 'transport':'https-jpeg-preview-v1'}
      frame = item[1]
      cursor = frame['stream'] + ':' + str(frame['sequence'])
      return {'available':True, 'frame':None if after == cursor else frame, 'cursor':cursor, 'transport':'https-jpeg-preview-v1'}


  def watch(self, device, camera):
    with self.lock:
      now = self.clock()
      self.leases = {key:expiry for key,expiry in self.leases.items() if expiry > now}
      if (device,camera) not in self.leases and len(self.leases) >= 64:
        raise ValueError("watch capacity")
      self.leases[(device,camera)] = now+15

  def requested(self, device):
    with self.lock:
      return sorted(camera for (owner,camera),expiry in self.leases.items() if owner == device and expiry > self.clock())

  def remaining(self, device):
    with self.lock:
      return max(0, min(15, int(max((expiry-self.clock() for (owner,_),expiry in self.leases.items() if owner == device), default=0))))


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
      if frame['source'] in ('wide-road','driver') and frame['source'] not in relay.requested(row['id']):
        raise ValueError('viewer lease expired')
      relay.put(row['id'], frame)
      return {'accepted':True, 'sequence':frame['sequence']}
    except (ValueError, KeyError, TypeError, AttributeError, OverflowError, InvalidSignature) as exc:
      raise HTTPException(403,'invalid media frame') from exc

  @app.get('/api/v1/devices/{device_id}/media')
  def preview(device_id: str, request: Request, after: str = '', camera: str = 'road-preview'):
    user = owner(request)
    row = store.get(device_id)
    if not row or row['state'] != 'paired' or row['owner_id'] != user['id']:
      raise HTTPException(404,'device not found')
    if len(after) > 80:
      raise HTTPException(400,'invalid media cursor')
    rate(request,'media-view:'+device_id,600)
    if camera not in ('road-preview','wide-road','driver'):
      raise HTTPException(400,'invalid camera')
    return relay.get(device_id, after, camera)

  @app.post('/api/v1/devices/{device_id}/media/watch')
  async def watch(device_id: str, request: Request):
    user = owner(request)
    row = store.get(device_id)
    if not row or row['state'] != 'paired' or row['owner_id'] != user['id']:
      raise HTTPException(404,'device not found')
    rate(request,'camera-watch:'+device_id,120)
    try:
      value = await request.json()
    except ValueError as exc:
      raise HTTPException(400,"invalid camera request") from exc
    if not isinstance(value,dict) or set(value) != {'camera'} or value['camera'] not in ('wide-road','driver'):
      raise HTTPException(400,'invalid camera')
    try:
      relay.watch(device_id,value['camera'])
    except ValueError as exc:
      raise HTTPException(429,'watch capacity') from exc
    return {'seconds':15}

  @app.post('/api/v1/agent/media/watch')
  async def requested(request: Request):
    rate(request,'camera-demand',1200)
    try:
      envelope = await request.json()
      row = store.get(envelope['device_id'])
      if not row or row['state'] != 'paired':
        raise ValueError('device unavailable')
      value = verify(envelope,row['public_key'],'media-watch')
      rate(request,'camera-demand:'+row['id'],60)
      if value['payload'] != {}:
        raise ValueError('invalid camera demand')
      store.consume_nonce(row['id'],value['nonce'])
      seconds = relay.remaining(row['id'])
      return {'cameras':relay.requested(row['id']) if seconds else [], 'seconds':seconds}
    except (ValueError,KeyError,TypeError,AttributeError,InvalidSignature) as exc:
      raise HTTPException(403,'invalid camera request') from exc
