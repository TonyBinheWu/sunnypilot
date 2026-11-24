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

  def finish(self, stamp, observed, reason):
    try:
      atomic_json(self.root / "lamp.json", {"stamp": stamp, "observed": observed, "reason": reason})
    except OSError:
      pass

  def reply(self, stamp, accepted, reason=None, *, setting=None, gear=None):
    try:
      receipt = {"stamp": stamp, "accepted": accepted, "reason": reason}
      if not accepted:
        if setting is not None:
          receipt["testSetting"] = setting
        if gear is not None:
          receipt["gear"] = gear
      atomic_json(self.root / "reply.json", receipt)
    except OSError:
      pass
