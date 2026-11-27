"""Local device pairing. QR credentials are fragments, never query parameters."""
import math
import re
import time
from urllib.parse import urlencode

import requests

from openpilot.sunnypilot.formosalink.identity import create, read
from openpilot.sunnypilot.formosalink.protocol import MAX_FRAME_BYTES, fingerprint, sign, validate_origin

DEFAULT_ORIGIN = "https://formosapilot.dinglu-t.com"


def pairing_url(origin, result):
  origin = validate_origin(origin)
  code, public_fingerprint, expires = result.get("pair_code"), result.get("fingerprint"), result.get("expires_at")
  if not isinstance(code, str) or not re.fullmatch(r"[A-F0-9]{12}", code):
    raise ValueError("invalid pairing code")
  if not isinstance(public_fingerprint, str) or not re.fullmatch(r"[a-f0-9]{24}", public_fingerprint):
    raise ValueError("invalid device fingerprint")
  if type(expires) not in (int, float) or not math.isfinite(expires) or not time.time() < expires <= time.time()+690:
    raise ValueError("invalid pairing expiry")
  return origin + "/#" + urlencode({"pair": code, "fp": public_fingerprint, "expires": int(expires)})


def response_json(response):
  response.raise_for_status()
  if len(response.content) > MAX_FRAME_BYTES:
    raise ValueError("oversized pairing response")
  result = response.json()
  if not isinstance(result, dict):
    raise ValueError("invalid pairing response")
  return result


def request_pairing(directory, origin=None):
  if origin is not None:
    origin = validate_origin(origin)
  try:
    identity, private, public = read(directory)
  except FileNotFoundError:
    try:
      identity, private, public = create(directory, origin or DEFAULT_ORIGIN)
    except FileExistsError:
      identity, private, public = read(directory)
  origin = origin or identity["origin"]
  if identity["origin"] != origin:
    raise ValueError("identity belongs to another server")
  result = response_json(requests.post(origin + "/api/v1/agent/enroll",
    json=sign(private, identity["device_id"], "enroll", {"public_key": public}), timeout=(5, 15)))
  if result.get("fingerprint") != fingerprint(public) or result.get("state") not in ("pending", "paired"):
    raise ValueError("invalid enrollment identity")
  return {**result, "url": pairing_url(origin, result) if result["state"] == "pending" else None}


def pairing_status(directory):
  identity, private, _ = read(directory)
  result = response_json(requests.post(identity["origin"] + "/api/v1/agent/status",
    json=sign(private, identity["device_id"], "status"), timeout=(5, 10)))
  if set(result) != {"state"} or result["state"] not in ("pending", "paired", "revoked"):
    raise ValueError("invalid device status")
  return result
