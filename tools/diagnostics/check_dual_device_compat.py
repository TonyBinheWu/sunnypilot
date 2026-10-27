"""Host-side C4/C3X regression checks, not an AGNOS or GPU hardware test.

Run once with BIG=0 EXPECTED_DEVICE=mici and again with BIG=1
EXPECTED_DEVICE=tizi. Only the UI process is started; no vehicle process runs.
"""
import json
import os
from pathlib import Path
import subprocess
import time
from types import SimpleNamespace
from typing import cast
import unittest
from unittest import mock

from openpilot.cereal import messaging
from openpilot.common.hardware.comma.hardware import get_device_type
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.test.helpers import processes_context

ROOT = Path(__file__).resolve().parents[2]


class TestDualDeviceCompat(OpenpilotTestCase):
  def test_agnos_version_manifest_and_legacy_paths(self):
    env = dict(os.environ)
    env.pop("AGNOS_VERSION", None)
    version = subprocess.check_output(
      ["bash", "-c", 'source ./launch_env.sh; printf "%s" "$AGNOS_VERSION"'], cwd=ROOT, env=env, text=True,
    )
    self.assertEqual(version, "19.9")
    manifest = ROOT / "openpilot/common/hardware/comma/agnos.json"
    # Pin the actual upstream manifest, not just a version string.
    blob = subprocess.check_output(["git", "hash-object", str(manifest)], cwd=ROOT, text=True).strip()
    self.assertEqual(blob, "96803bdb859c53b6ef3130c683f7730164c7daff")
    self.assertEqual({p["name"] for p in json.loads(manifest.read_text())},
                     {"xbl", "xbl_config", "abl", "aop", "devcfg", "boot", "system"})
    for alias in ("system/hardware/tici/agnos.json", "openpilot/system/hardware/comma/agnos.json"):
      with self.subTest(alias=alias):
        self.assertEqual((ROOT / alias).resolve(strict=True), manifest.resolve(strict=True))
    subprocess.run(["bash", "-n", "launch_env.sh", "launch_chffrplus.sh"], cwd=ROOT, check=True)

  def test_device_identity_is_not_forced(self):
    for device in ("mici", "tizi"):
      with self.subTest(device=device):
        get_device_type.cache_clear()
        try:
          with mock.patch("builtins.open", mock.mock_open(read_data=f"comma {device}\x00")) as opened:
            self.assertEqual(get_device_type(), device)
            opened.assert_called_once_with("/sys/firmware/devicetree/base/model")
        finally:
          get_device_type.cache_clear()

  def test_ui_profile_selection(self):
    from openpilot.selfdrive.ui import ui
    from openpilot.system.ui.lib.application import gui_app
    device = os.environ["EXPECTED_DEVICE"]
    self.assertIn(device, ("mici", "tizi"))  # codespell:ignore assertin
    expected_big = device == "tizi"
    self.assertEqual(os.environ["BIG"], "1" if expected_big else "0")
    self.assertEqual(gui_app.big_ui(), expected_big)
    self.assertEqual(ui.BIG_UI, expected_big)

  def test_custom_stop_marker_status_branches(self):
    from openpilot.selfdrive.ui.onroad import model_renderer as renderer
    from openpilot.selfdrive.ui.ui_state import UIStatus
    import pyray as rl

    class FakeSubMaster(dict):
      recv_frame = {"extrinsicsCalibration": 10, "modelV2": 10}
      updated = {"carParams": False, "modelV2": False, "radarState": False}
      valid = {"radarState": False}

    sm = FakeSubMaster(selfdriveState=SimpleNamespace(experimentalMode=False),
                      extrinsicsCalibration=SimpleNamespace(height=[1.22]), modelV2=object())
    rect = rl.Rectangle(0, 0, 100, 100)
    for status in UIStatus:
      with self.subTest(status=status):
        marker = mock.Mock()
        view = SimpleNamespace(_counter=1, _longitudinal_control=False, _transform_dirty=False,
                               _draw_lane_lines=mock.Mock(), _draw_path=mock.Mock(), predicted_stop_marker=marker,
                               _rect=rect, _path=object(), _map_to_screen=mock.Mock())
        state = SimpleNamespace(sm=sm, started_frame=0, status=status)
        with mock.patch.object(renderer, "ui_state", state):
          renderer.ModelRenderer._render(cast(renderer.ModelRenderer, view), rect)
        if status in (UIStatus.ENGAGED, UIStatus.LAT_ONLY):
          marker.render.assert_called_once()
          marker.reset.assert_not_called()
        else:
          marker.reset.assert_called_once()
          marker.render.assert_not_called()

  def test_ui_process_produces_frames(self):
    sock = messaging.sub_sock("uiDebug", conflate=False, timeout=100)
    with processes_context(["ui"]) as processes:
      frames = []
      deadline = time.monotonic() + 15
      while len(frames) < 5 and time.monotonic() < deadline:
        self.assertIsNone(processes[0].proc.exitcode, "UI exited before rendering frames")
        frames.extend(messaging.drain_sock(sock))
        time.sleep(0.02)
      self.assertGreaterEqual(len(frames), 5, "UI did not publish enough rendered-frame messages")
      self.assertTrue(all(frame.valid for frame in frames))


if __name__ == "__main__":
  unittest.main(verbosity=2)
