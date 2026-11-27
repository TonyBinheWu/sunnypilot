import base64
import json
import os
import uuid
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from openpilot.sunnypilot.formosalink.protocol import public_key_text
from openpilot.sunnypilot.formosalink.service_policy import self_hosted_origin as validate_origin


def default_directory():
  return Path(os.environ.get("FORMOSALINK_STATE_DIR", "/data/formosalink"))


def create(directory, origin):
  directory = Path(directory)
  origin = validate_origin(origin)
  directory.mkdir(parents=True, exist_ok=True, mode=0o700)
  private = Ed25519PrivateKey.generate()
  raw = private.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
  value = {"device_id": str(uuid.uuid4()), "origin": origin, "private_key": base64.b64encode(raw).decode()}
  path = directory / "identity.json"
  # Never replace a registered identity implicitly.
  with path.open("x", encoding="utf-8") as file:
    os.chmod(path, 0o600)
    json.dump(value, file)
  return read(directory)


def read(directory):
  value = json.loads((Path(directory) / "identity.json").read_text(encoding="utf-8"))
  value["origin"] = validate_origin(value["origin"])
  uuid.UUID(value["device_id"])
  private = Ed25519PrivateKey.from_private_bytes(base64.b64decode(value["private_key"], validate=True))
  return value, private, public_key_text(private)
