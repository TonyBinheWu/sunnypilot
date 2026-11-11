"""Self-hosted, owner-only MJPEG over WebSocket. Latest frame only, never a history."""
import asyncio
import json
import time
from urllib.parse import urlparse

from cryptography.exceptions import InvalidSignature
from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from openpilot.sunnypilot.formosalink.media_protocol import MAX_MEDIA_BYTES, validate_frame
from openpilot.sunnypilot.formosalink.protocol import MAX_FRAME_BYTES, verify

CAMERAS = ('wide-road', 'driver')


class StreamHub:
  def __init__(self):
    self.publishers = {}
    self.viewers = {}

  def push(self, key, frame):
    for queue in self.viewers.get(key, ()):
      if queue.full():
        queue.get_nowait()
      queue.put_nowait((time.monotonic(), frame))


def register(app, store, owner, rate, origin, relay):
  hub = app.state.streams = StreamHub()
  authority = urlparse(origin).netloc.lower()

  def host_ok(socket):
    return socket.headers.get('host', '').lower() == authority

  def owned(socket, device, user_id):
    user = owner(socket)
    row = store.get(device)
    if user['id'] != user_id or not row or row['state'] != 'paired' or row['owner_id'] != user_id:
      raise ValueError('ownership changed')

  @app.websocket('/api/v1/media/probe')
  async def probe(socket: WebSocket):
    # Public transport check exposes no device IDs, users, credentials or media.
    try:
      if not host_ok(socket) or socket.headers.get('origin') not in (None, origin):
        raise ValueError('invalid probe origin')
      rate(socket, 'stream-probe', 30)
      await socket.accept()
      await socket.send_json({'service':'FormosaLink', 'transport':'wss-mjpeg-v1', 'fps':8})
      await socket.close()
    except (ValueError, HTTPException):
      await socket.close(code=1008)
    except (WebSocketDisconnect, OSError):
      pass

  @app.websocket('/api/v1/devices/{device_id}/media/stream')
  async def viewer(socket: WebSocket, device_id: str, camera: str = 'wide-road'):
    queue, key = asyncio.Queue(maxsize=1), (device_id, camera)
    accepted = False
    try:
      if not host_ok(socket) or socket.headers.get('origin') != origin or camera not in CAMERAS:
        raise ValueError('invalid viewer origin or camera')
      user_id = owner(socket)['id']
      owned(socket, device_id, user_id)
      rate(socket, 'stream-open:'+device_id, 60)
      if sum(map(len, hub.viewers.values())) >= 64 or len(hub.viewers.get(key, ())) >= 4:
        raise ValueError('viewer capacity')
      hub.viewers.setdefault(key, set()).add(queue)
      await socket.accept()
      accepted = True
      while True:
        owned(socket, device_id, user_id)
        relay.watch(device_id, camera)
        try:
          received, frame = await asyncio.wait_for(queue.get(), timeout=1)
          if time.monotonic()-received > 1 or abs(time.time()-frame['sampled_at']) > 3:
            continue
          message = {'type':'frame', 'frame':frame}
        except asyncio.TimeoutError:
          message = {'type':'waiting'}
        # Recheck after the wait as logout/unpair may have happened meanwhile.
        owned(socket, device_id, user_id)
        await asyncio.wait_for(socket.send_json(message), timeout=2)
        raw = await asyncio.wait_for(socket.receive_text(), timeout=3)
        if len(raw) > 64 or json.loads(raw) != {'type':'ack'}:
          raise ValueError('invalid viewer acknowledgement')
    except asyncio.TimeoutError:
      try:
        await socket.close(code=1013)
      except (RuntimeError, WebSocketDisconnect):
        pass
    except (ValueError, KeyError, TypeError, HTTPException):
      try:
        await socket.close(code=1008 if not accepted else 4003)
      except (RuntimeError, WebSocketDisconnect):
        pass
    except (WebSocketDisconnect, OSError):
      pass
    finally:
      viewers = hub.viewers.get(key)
      if viewers is not None:
        viewers.discard(queue)
        if not viewers:
          hub.viewers.pop(key, None)
          # Do not discard a separate legacy HTTP viewer's short lease.

  @app.websocket('/api/v1/agent/media/stream')
  async def publisher(socket: WebSocket):
    key = None
    try:
      if not host_ok(socket) or socket.headers.get('origin'):
        raise ValueError('invalid agent origin')
      rate(socket, 'stream-auth', 120)
      if len(hub.publishers) >= 32:
        raise ValueError('publisher capacity')
      await socket.accept()
      raw = await asyncio.wait_for(socket.receive_text(), timeout=5)
      if len(raw.encode()) > MAX_FRAME_BYTES:
        raise ValueError('oversized authentication')
      envelope = json.loads(raw)
      row = store.get(envelope['device_id'])
      if not row or row['state'] != 'paired':
        raise ValueError('unpaired device')
      value = verify(envelope, row['public_key'], 'media-stream')
      if not isinstance(value['payload'], dict) or set(value['payload']) != {'camera'}:
        raise ValueError('invalid stream request')
      camera = value['payload']['camera']
      if camera not in CAMERAS or camera not in relay.requested(row['id']):
        raise ValueError('no owner viewer')
      store.consume_nonce(row['id'], value['nonce'])
      key = (row['id'], camera)
      if key in hub.publishers:
        raise ValueError('camera already streaming')
      hub.publishers[key] = socket
      await socket.send_json({'type':'ready', 'fps':8, 'transport':'wss-mjpeg-v1'})
      previous, stream, last_received = -1, None, 0
      while True:
        raw = await asyncio.wait_for(socket.receive_text(), timeout=5)
        now = time.monotonic()
        if len(raw.encode()) > MAX_MEDIA_BYTES or now-last_received < .06:
          raise ValueError('oversized or excessive stream')
        current = store.get(row['id'])
        if not current or current['state'] != 'paired' or current['owner_id'] != row['owner_id'] or camera not in relay.requested(row['id']):
          raise ValueError('viewer expired or device revoked')
        frame = validate_frame(json.loads(raw))
        if frame['source'] != camera or frame['sequence'] <= previous or stream is not None and frame['stream'] != stream:
          raise ValueError('invalid camera sequence')
        previous, stream, last_received = frame['sequence'], frame['stream'], now
        relay.put(row['id'], frame)
        hub.push(key, frame)
        await asyncio.wait_for(socket.send_json({'type':'ack', 'sequence':previous}), timeout=2)
    except (ValueError, KeyError, TypeError, AttributeError, InvalidSignature, HTTPException, asyncio.TimeoutError):
      try:
        await socket.close(code=1008)
      except (RuntimeError, WebSocketDisconnect):
        pass
    except (WebSocketDisconnect, OSError):
      pass
    finally:
      if key and hub.publishers.get(key) is socket:
        hub.publishers.pop(key, None)
