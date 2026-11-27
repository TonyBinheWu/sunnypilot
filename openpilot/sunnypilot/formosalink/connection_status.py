"""Only a server-acknowledged telemetry frame marks this companion online."""
import json
import os
from pathlib import Path
import tempfile
import time


def status_path():
  return Path(os.environ.get("FORMOSALINK_STATUS_PATH", "/dev/shm/formosalink-status.json"))


def acknowledge(origin):
  path = status_path()
  temporary = None
  try:
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
      temporary = stream.name
      json.dump({"origin":origin, "last_ack":time.monotonic()}, stream)
    os.replace(temporary, path)
  except OSError:
    pass  # A status display failure must not interrupt telemetry.
  finally:
    if temporary:
      try:
        os.unlink(temporary)
      except OSError:
        pass


def is_online(origin, now=None):
  try:
    state = json.loads(status_path().read_text())
    stamp = state.get("last_ack")
    return (state.get("origin") == origin and type(stamp) in (int, float) and
            0 <= (time.monotonic() if now is None else now)-stamp <= 20)
  except (OSError, ValueError, TypeError, AttributeError):
    return False
