"""Short-lived, parked-only requests from the vehicle settings page."""
import math
import time
from pathlib import Path

from openpilot.selfdrive.carrot.bluetooth.model import atomic_json, read_json

ROOT = Path("/dev/shm/carrot-parked-indicator")
DURATION = 7.
ACCEPT_WINDOW = .5


class ParkedIndicator:
  def __init__(self, root=ROOT):
    self.root = root
    self.started = time.monotonic()
    self.seen = None

  def take(self, now):
    message = read_json(self.root / "request.json", {})
    if not isinstance(message, dict):
      return None
    stamp, side = message.get("stamp"), message.get("side")
    if type(stamp) not in (float, int) or not math.isfinite(stamp) or side not in ("left", "right"):
      return None
    if self.seen == stamp or stamp < self.started or not 0 <= now - stamp < ACCEPT_WINDOW:
      return None
    self.seen = stamp
    return stamp, side

  def reply(self, stamp, accepted):
    try:
      atomic_json(self.root / "reply.json", {"stamp": stamp, "accepted": accepted})
    except OSError:
      pass
