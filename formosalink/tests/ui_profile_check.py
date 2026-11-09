"""Native Linux integration checks common to both maintained branches.

BIG=1 EXPECTED_DEVICE=tizi for C3X layout, BIG=0 EXPECTED_DEVICE=mici for C4.
These PC profiles do not emulate the physical devices or their inference backend.
"""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from openpilot.cereal import messaging
from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase

ROOT = Path(__file__).resolve().parents[2]


class TestSharedProfile(OpenpilotTestCase):
  def test_profile_selection(self):
    from openpilot.system.ui.lib.application import gui_app
    from openpilot.selfdrive.ui import ui
    device = os.environ["EXPECTED_DEVICE"]
    self.assertIn(device, ("tizi", "mici"))
    expected = device == "tizi"
    self.assertEqual(os.environ["BIG"], "1" if expected else "0")
    self.assertEqual(gui_app.big_ui(), expected)
    self.assertEqual(ui.BIG_UI, expected)

  def test_agent_disabled_by_default(self):
    self.assertFalse(Params().get_bool("FormosaLinkEnabled"))

  def test_agnos_platform_configuration(self):
    device = os.environ["EXPECTED_DEVICE"]
    env = dict(os.environ)
    env.pop("AGNOS_VERSION", None)
    env.pop("AGNOS_MANIFEST", None)
    with tempfile.TemporaryDirectory() as directory:
      model = Path(directory) / "model"
      model.write_bytes(f"comma {device}\0".encode())
      env["AGNOS_DEVICE_MODEL_PATH"] = str(model)
      version, manifest = subprocess.check_output(["bash","-c",'source ./launch_env.sh && printf "%s\\n%s\\n" "$AGNOS_VERSION" "$AGNOS_MANIFEST"'],cwd=ROOT,env=env,text=True).strip().splitlines()
    self.assertEqual(version, "19.9" if device == "tizi" else "20.1")
    digest = subprocess.check_output(["git","hash-object",str(ROOT/manifest)],cwd=ROOT,text=True).strip()
    self.assertEqual(digest,"96803bdb859c53b6ef3130c683f7730164c7daff" if device=="tizi" else "4e90e7c8d82388f02078fffa8ddd928afebbc784")
    self.assertTrue(json.loads((ROOT/manifest).read_text()))

  def test_real_ui_frame_emission(self):
    sock = messaging.sub_sock("uiDebug",conflate=False,timeout=100)
    process = subprocess.Popen([sys.executable,"-m","openpilot.selfdrive.ui.ui"],cwd=ROOT)
    try:
      frames=[]
      deadline=time.monotonic()+15
      while len(frames)<5 and time.monotonic()<deadline:
        self.assertIsNone(process.poll(),"UI exited before emitting frames")
        frames.extend(messaging.drain_sock(sock))
        time.sleep(.02)
      self.assertGreaterEqual(len(frames),5)
      self.assertTrue(all(math.isfinite(frame.uiDebug.frameTimeMillis) for frame in frames))
      self.assertEqual(sorted(frame.logMonoTime for frame in frames),[frame.logMonoTime for frame in frames])
    finally:
      process.terminate()
      try:
        process.wait(timeout=5)
      except subprocess.TimeoutExpired:
        process.kill();process.wait(timeout=5)


if __name__ == "__main__":
  unittest.main(verbosity=2)
