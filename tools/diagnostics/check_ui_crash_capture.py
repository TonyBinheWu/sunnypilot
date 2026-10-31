"""Test persistent Python/thread/native crash capture without vehicle hardware."""
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from openpilot.system.manager.ui_crash import capture_ui_crashes, record_event


class TestCapture(unittest.TestCase):
  def test_exception_not_swallowed_and_rotated(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      for i in range(4):
        with self.assertRaisesRegex(ValueError, str(i)):
          with capture_ui_crashes(root, commit=str(i)):
            raise ValueError(f"fixture {i}")
      self.assertEqual(len(list(root.glob("ui.log*"))), 3)
      for name, i in [("ui.log", 3), ("ui.log.1", 2), ("ui.log.2", 1)]:
        self.assertTrue(f"fixture {i}" in (root / name).read_text())
      self.assertEqual((root / "ui.log").stat().st_mode & 0o777, 0o600)

  def test_unwritable_capture_does_not_block_ui(self):
    with tempfile.NamedTemporaryFile() as f:
      with capture_ui_crashes(Path(f.name) / "bad"):
        pass
      record_event(Path(f.name) / "bad", "exit")

  def test_thread_failure_recorded_and_hook_restored(self):
    with tempfile.TemporaryDirectory() as tmp:
      original = threading.excepthook
      with patch("threading.excepthook") as previous:
        with capture_ui_crashes(Path(tmp)):
          def fail():
            raise RuntimeError("parameter-refresh-error")
          t = threading.Thread(target=fail, name="params")
          t.start()
          t.join()
        self.assertIs(threading.excepthook, previous)
        previous.assert_called_once()
      self.assertIs(threading.excepthook, original)
      self.assertTrue("parameter-refresh-error" in (Path(tmp) / "ui.log").read_text())

  def test_native_abort_captured(self):
    with tempfile.TemporaryDirectory() as tmp:
      code = ("import os, resource; from pathlib import Path; "
              "from openpilot.system.manager.ui_crash import capture_ui_crashes; "
              "resource.setrlimit(resource.RLIMIT_CORE, (0, 0))\n"
              f"with capture_ui_crashes(Path({tmp!r})):\n os.abort()\n")
      proc = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=10, check=False)
      self.assertEqual(proc.returncode, -signal.SIGABRT)
      self.assertTrue("Fatal Python error: Aborted" in (Path(tmp) / "ui.log").read_text())

  def test_events_bounded(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root / "events.jsonl").write_text("x" * 65537)
      record_event(root, "ui_exit", exitcode=-9, onroad=True)
      event = json.loads((root / "events.jsonl").read_text())
      self.assertEqual(event["exitcode"], -9)
      self.assertTrue((root / "events.jsonl.1").exists())


if __name__ == "__main__":
  unittest.main(verbosity=2)
