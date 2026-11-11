"""Keep the Carrot integration independent of sunnypilot-only settings/model APIs."""
from pathlib import Path
import time
import uuid

CARROT = (Path(__file__).resolve().parents[2] / "selfdrive/carrot/carrot_server.py").is_file()


class CarrotStatusProvider:
  """Read-only portal health; Carrot writes go through its own web interface."""
  def __init__(self):
    from openpilot.common.params import Params
    from openpilot.cereal import messaging
    self.params = Params()
    self.sm = messaging.SubMaster(["deviceState", "carState", "pandaStates"])
    self.session = str(uuid.uuid4())

  def capture(self):
    from openpilot.sunnypilot.formosalink.settings import revision
    from openpilot.sunnypilot.formosalink.telemetry import source_valid
    from openpilot.sunnypilot.formosalink.device_health import collect_health
    self.sm.update(0)
    parked = bool(source_valid(self.sm, "deviceState", 2) and self.params.get_bool("IsOffroad") and not self.sm["deviceState"].started)
    catalog_hash = revision([])
    from openpilot.sunnypilot.formosalink.camera_status import snapshot as camera_snapshot
    return {"version": 1, "session": self.session, "sampled_at": time.time(), "offroad": parked, "remote_enabled": False,
            "catalog_revision": catalog_hash, "revision": revision({"catalog": catalog_hash, "values": {}}),
            "catalog": [], "values": {}, "info": {**collect_health(self.sm, "unknown"), **camera_snapshot()}, "receipts": []}

  def apply(self, command, device_id, deadline):
    return {"id": command["id"], "status": "rejected", "reason": "permission_disabled"}
