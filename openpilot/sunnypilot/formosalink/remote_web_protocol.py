"""Bounded transport to the device's fixed loopback Carrot server."""
import base64
from urllib.parse import unquote, urlsplit

SERVICE = "carrot-web-v1"
MAX_BODY = 8 * 1024 * 1024
MAX_MESSAGE = 12 * 1024 * 1024
CHUNK_SIZE = 32 * 1024
MAX_CHANNELS = 16
REQUEST_HEADERS = frozenset(("content-type", "range", "if-range", "accept", "authorization", "content-encoding", "sec-fetch-site"))
RESPONSE_HEADERS = frozenset(("content-type", "content-range", "accept-ranges", "content-disposition", "location"))


def target_path(value):
  if not isinstance(value, str) or len(value) > 8192 or any(ord(c) < 32 for c in value) or "\\" in value:
    raise ValueError("invalid target")
  parsed = urlsplit(value)
  if parsed.scheme or parsed.netloc or parsed.fragment or not value.startswith("/") or value.startswith("//"):
    raise ValueError("loopback path required")
  decoded = parsed.path
  for _ in range(3):
    decoded = unquote(decoded)
  if decoded.startswith("//") or "\\" in decoded or any(part in (".", "..") for part in decoded.split("/")):
    raise ValueError("unsafe target path")
  if any(ord(c) < 32 for c in decoded):
    raise ValueError("invalid target path")
  return value


def decode_body(value, maximum=MAX_BODY):
  if not isinstance(value, str) or len(value) > (maximum + 2) // 3 * 4:
    raise ValueError("body too large")
  body = base64.b64decode(value, validate=True)
  if len(body) > maximum:
    raise ValueError("body too large")
  return body


def headers(values, allowed):
  if not isinstance(values, dict) or len(values) > 40:
    raise ValueError("invalid headers")
  result = {}
  for name, value in values.items():
    if not isinstance(name, str) or not isinstance(value, str) or len(value) > 8192 or "\r" in value or "\n" in value:
      raise ValueError("invalid header")
    if name.lower() in allowed:
      result[name.lower()] = value
  return result
