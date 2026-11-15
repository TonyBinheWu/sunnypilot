"""Protocol v1. Kept free of openpilot runtime imports for cloud/host tests."""
import base64
import json
import math
import time
import uuid
from urllib.parse import urlparse

VERSION = 1
AGENT_VERSION = "0.1.0"
MAX_FRAME_BYTES = 16384
MAX_CLOCK_SKEW = 90
SAMPLE_INTERVAL = 5
ONLINE_SECONDS = 20
METRIC_KEYS = {
  "started", "speed_kph", "cpu_temp_c", "gpu_temp_c", "memory_percent", "free_space_percent",
  "thermal_status", "device_type", "software_version", "branch", "commit", "sample_valid",
}


def canonical(value):
  return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def validate_origin(origin):
  parsed = urlparse(origin)
  if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
    raise ValueError("origin must be an HTTPS origin")
  if parsed.scheme == "http" and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
    raise ValueError("HTTP is allowed only on loopback for development")
  if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
    raise ValueError("use a dedicated site origin, without a path, query or fragment")
  return origin.rstrip("/")


def public_key_text(private_key):
  from cryptography.hazmat.primitives import serialization
  raw = private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
  return base64.b64encode(raw).decode()


def fingerprint(public_key):
  import hashlib
  return hashlib.sha256(base64.b64decode(public_key, validate=True)).hexdigest()[:24]


def sign(private_key, device_id, purpose, payload=None, timestamp=None, nonce=None):
  body = {"version": VERSION, "device_id": device_id, "purpose": purpose, "payload": payload or {},
          "timestamp": int(time.time() if timestamp is None else timestamp), "nonce": nonce or str(uuid.uuid4())}
  return {**body, "signature": base64.b64encode(private_key.sign(canonical(body))).decode()}


def verify(envelope, public_key, purpose, now=None):
  from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
  expected = {"version", "device_id", "purpose", "payload", "timestamp", "nonce", "signature"}
  if not isinstance(envelope, dict) or set(envelope) != expected:
    raise ValueError("invalid envelope")
  body = {k: v for k, v in envelope.items() if k != "signature"}
  if body["version"] != VERSION or body["purpose"] != purpose:
    raise ValueError("unsupported protocol or purpose")
  uuid.UUID(body["device_id"])
  uuid.UUID(body["nonce"])
  if type(body["timestamp"]) is not int or abs((time.time() if now is None else now) - body["timestamp"]) > MAX_CLOCK_SKEW:
    raise ValueError("expired authentication; check device clock")
  if not isinstance(body["payload"], dict):
    raise ValueError("invalid payload")
  key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key, validate=True))
  key.verify(base64.b64decode(envelope["signature"], validate=True), canonical(body))
  return body


def validate_snapshot(data):
  if not isinstance(data, dict) or set(data) != {"version", "sequence", "sampled_at", "metrics"}:
    raise ValueError("invalid snapshot")
  if data["version"] != VERSION or type(data["sequence"]) is not int or data["sequence"] < 0:
    raise ValueError("invalid sequence/version")
  if type(data["sampled_at"]) not in (int, float) or not math.isfinite(data["sampled_at"]):
    raise ValueError("invalid sample time")
  metrics = data["metrics"]
  if not isinstance(metrics, dict) or not set(metrics) <= METRIC_KEYS:
    raise ValueError("only explicitly allowed telemetry is accepted")
  if type(metrics.get("sample_valid")) is not bool:
    raise ValueError("sample validity is required")
  for key, value in metrics.items():
    if value is None:
      continue
    if key in {"started", "sample_valid"}:
      if type(value) is not bool:
        raise ValueError("invalid boolean")
    elif key in {"speed_kph", "cpu_temp_c", "gpu_temp_c", "memory_percent", "free_space_percent"}:
      if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("invalid numeric metric")
      if key in {"memory_percent", "free_space_percent"} and not 0 <= value <= 100:
        raise ValueError("percentage out of range")
      if key == "speed_kph" and not 0 <= value <= 500:
        raise ValueError("speed out of range")
      if key.endswith("temp_c") and not -100 <= value <= 250:
        raise ValueError("temperature out of range")
    elif not isinstance(value, str) or len(value) > 160:
      raise ValueError("invalid text metric")
  canonical(data)
  return data
