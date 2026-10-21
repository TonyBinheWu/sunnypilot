"""ccNC display settings must remain opt-in, gated and defined in the frontend schema."""
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import generate_schema
from openpilot.sunnypilot.sunnylink.capabilities import CAPABILITY_FIELDS


CCNC_KEYS = (
  "CcncClusterDisplayEnabled",
  "CcncClusterAssistIcons",
  "CcncClusterLaneGuidance",
  "CcncClusterSurroundingObjects",
  "CcncClusterTrafficSigns",
)


class TestCcncClusterSettings(OpenpilotTestCase):
  def test_all_settings_gated_by_validated_protocol(self):
    data = generate_schema()
    visuals = next(p for p in data["panels"] if p["id"] == "visuals")
    section = next(s for s in visuals["sections"] if s["id"] == "ccnc_cluster")
    self.assertEqual(tuple(item["key"] for item in section["items"]), CCNC_KEYS)
    self.assertIn("ccnc_cluster_verified", CAPABILITY_FIELDS)
    for item in section["items"]:
      self.assertIn({"type": "capability", "field": "ccnc_cluster_verified", "equals": True}, item["enablement"])
      self.assertIn({"type": "offroad_only"}, item["enablement"])

  def test_subsections_require_master_switch(self):
    data = generate_schema()
    visuals = next(p for p in data["panels"] if p["id"] == "visuals")
    section = next(s for s in visuals["sections"] if s["id"] == "ccnc_cluster")
    for item in section["items"][1:]:
      self.assertIn({"type": "param", "key": CCNC_KEYS[0], "equals": True}, item["enablement"])
