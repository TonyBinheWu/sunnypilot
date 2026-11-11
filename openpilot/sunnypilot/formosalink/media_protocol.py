"""Phase 1 signed JPEG preview transport. No native imports or control messages."""
import base64
import math
import time
import uuid

MAX_MEDIA_BYTES = 262144
MAX_JPEG_BYTES = 180000
MEDIA_TTL = 3


def jpeg_size(data):
  if not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'):
    raise ValueError('invalid JPEG')
  at = 2
  while at + 4 <= len(data):
    if data[at] != 255:
      raise ValueError('invalid JPEG marker')
    marker = data[at + 1]
    at += 2
    size = int.from_bytes(data[at:at + 2], 'big')
    if size < 2 or at + size > len(data):
      raise ValueError('invalid JPEG segment')
    if marker in (0xc0, 0xc1, 0xc2):
      if size < 8:
        raise ValueError('invalid JPEG dimensions')
      return int.from_bytes(data[at + 5:at + 7], 'big'), int.from_bytes(data[at + 3:at + 5], 'big')
    if marker == 0xda:
      break
    at += size
  raise ValueError('missing JPEG dimensions')


def validate_frame(value, now=None):
  fields = {'version', 'stream', 'sequence', 'sampled_at', 'source', 'width', 'height', 'jpeg', 'hud'}
  if not isinstance(value, dict) or set(value) != fields or type(value['version']) is not int or value['version'] != 1:
    raise ValueError('invalid media frame')
  uuid.UUID(value['stream'])
  if type(value['sequence']) is not int or not 0 <= value['sequence'] < 2**53:
    raise ValueError('invalid media sequence')
  sampled = value['sampled_at']
  if type(sampled) not in (int, float) or not math.isfinite(sampled) or abs((time.time() if now is None else now) - sampled) > MEDIA_TTL:
    raise ValueError('expired media frame')
  if value['source'] not in ('demo', 'road-preview', 'wide-road', 'driver'):
    raise ValueError('unsupported media source')
  if any(type(value[k]) is not int for k in ('width','height')) or not 1 <= value['width'] <= 1280 or not 1 <= value['height'] <= 720:
    raise ValueError('invalid media dimensions')
  if not isinstance(value['jpeg'], str) or len(value['jpeg']) > MAX_JPEG_BYTES * 4 // 3 + 4:
    raise ValueError('oversized media frame')
  data = base64.b64decode(value['jpeg'], validate=True)
  if len(data) > MAX_JPEG_BYTES or jpeg_size(data) != (value['width'], value['height']):
    raise ValueError('invalid media image')
  hud = value['hud']
  if not isinstance(hud, dict) or set(hud) != {'speed_kph', 'engaged'}:
    raise ValueError('invalid media HUD')
  if hud['engaged'] is not None and type(hud['engaged']) is not bool:
    raise ValueError('invalid engagement')
  speed = hud['speed_kph']
  if speed is not None and (type(speed) not in (int,float) or not math.isfinite(speed) or not 0 <= speed <= 500):
    raise ValueError('invalid media speed')
  return value
