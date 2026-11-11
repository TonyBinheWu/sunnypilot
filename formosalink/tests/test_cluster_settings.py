"""The remote display switch follows native capability and parked guards."""
import json
from pathlib import Path

import pytest

from openpilot.sunnypilot.formosalink.settings import catalog


@pytest.mark.parametrize("supported", [False, True])
@pytest.mark.parametrize("parked", [False, True])
def test_display_catalog_requires_observed_capability_and_parked(supported, parked):
  schema = json.loads(Path("openpilot/sunnypilot/sunnylink/settings_ui.json").read_text(encoding="utf-8"))
  key = "FormosaClusterDisplay"
  rows = catalog(schema, {key: False}, {key: "BOOL"}, {"brand": "hyundai", "formosa_cluster_supported": supported}, parked)
  item = next(row for row in rows if row["key"] == key)
  assert item["enabled"] is (supported and parked)
  assert set(item["description"]) == {"zh-TW", "en", "ja"}
  assert len(set(item["description"].values())) == 3
  assert all(item["title"].values())
  assert "Restart" in item["description"]["en"]
