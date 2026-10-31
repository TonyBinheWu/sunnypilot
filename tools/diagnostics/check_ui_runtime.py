"""UI lifecycle tests. No manager loop, camera or vehicle-control process starts."""
import json
import multiprocessing
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from openpilot.system.manager.process import PythonProcess, join_process, launcher
from openpilot.system.manager.ui_process import C3xUIProcess, RETRY_DELAYS, make_ui_process


class TestUIRecovery(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    root_patch = mock.patch("openpilot.system.manager.ui_process.crash_root", return_value=Path(self.tmp.name))
    root_patch.start()
    self.addCleanup(root_patch.stop)

  @staticmethod
  def dead_process(pid):
    proc = mock.Mock(pid=pid, exitcode=-11)
    proc.is_alive.return_value = False
    return proc

  def test_only_c3x_uses_recovery(self):
    self.assertIsInstance(make_ui_process("tizi"), C3xUIProcess)
    for device in ("mici", "tici", "pc"):
      with self.subTest(device=device):
        proc = make_ui_process(device)
        self.assertIs(type(proc), PythonProcess)
        self.assertIs(proc.launcher, launcher)
        self.assertTrue(proc.should_run(True, None, None))
        self.assertTrue(proc.should_run(False, None, None))

  def test_upstream_process_does_not_restart_after_exit(self):
    proc = PythonProcess("ui", "openpilot.selfdrive.ui.ui", lambda *args: True)
    exited = self.dead_process(100)
    proc.proc = exited
    with mock.patch("openpilot.system.manager.process.Process") as spawn:
      proc.start()
      spawn.assert_not_called()
    self.assertIs(proc.proc, exited)

  def test_no_restart_onroad_and_delayed_offroad_restart(self):
    proc = C3xUIProcess()
    exited = self.dead_process(101)
    proc.proc = exited
    proc.should_run(True, None, None)
    with mock.patch.object(PythonProcess, "start") as start, \
         mock.patch("openpilot.system.manager.ui_process.time.monotonic", return_value=0.0) as clock:
      proc.start()
      clock.return_value = 100.0
      proc.start()
      start.assert_not_called()
      self.assertIs(proc.proc, exited)
      self.assertEqual(proc.get_process_state_msg().exitCode, -11)
      proc.should_run(False, None, None)
      proc.start()
      start.assert_called_once()
      self.assertIsNone(proc.proc)
      self.assertEqual(proc._restarts, 1)

  def test_restart_budget_and_backoff(self):
    proc = C3xUIProcess()
    proc.should_run(False, None, None)
    with mock.patch.object(PythonProcess, "start") as start, \
         mock.patch("openpilot.system.manager.ui_process.time.monotonic", return_value=0.0) as clock:
      for index, delay in enumerate(RETRY_DELAYS):
        proc.proc = self.dead_process(200 + index)
        clock.return_value = 100.0 * index
        proc.start()
        self.assertEqual(start.call_count, index)
        clock.return_value += delay - 0.01
        proc.start()
        self.assertEqual(start.call_count, index)
        clock.return_value += 0.02
        proc.start()
        self.assertEqual(start.call_count, index + 1)
      exited = self.dead_process(300)
      proc.proc = exited
      clock.return_value = 10000.0
      proc.start()
      clock.return_value += 10000.0
      proc.start()
      self.assertEqual(start.call_count, len(RETRY_DELAYS))
      self.assertIs(proc.proc, exited)

  @unittest.skipUnless(multiprocessing.get_start_method() == "fork", "Requires inherited test-only crash-root override")
  def test_real_child_crash_is_recorded_and_retries_are_bounded(self):
    root = Path(self.tmp.name)
    (root / "ui_crash_probe.py").write_text('def main():\n  raise RuntimeError("controlled-ui-crash")\n')
    proc = C3xUIProcess()
    proc.module = "ui_crash_probe"
    proc.should_run(False, None, None)
    pids = []
    try:
      with mock.patch.object(sys, "path", [str(root), *sys.path]), \
           mock.patch("openpilot.system.manager.ui_process.RETRY_DELAYS", (0.0, 0.0, 0.0)):
        for _ in range(4):
          proc.start()
          self.assertIsNotNone(proc.proc)
          pids.append(proc.proc.pid)
          join_process(proc.proc, 5)
          self.assertIsNotNone(proc.proc.exitcode, "Test child did not exit")
          self.assertNotEqual(proc.proc.exitcode, 0)
        last = proc.proc
        proc.start()
        self.assertIs(proc.proc, last)
        self.assertEqual(len(set(pids)), 4)
        self.assertEqual(proc._restarts, 3)
      self.assertTrue("controlled-ui-crash" in (root / "ui.log").read_text())
      events = [json.loads(line) for line in (root / "events.jsonl").read_text().splitlines()]
      self.assertEqual(sum(e["event"] == "ui_offroad_restart" for e in events), 3)
    finally:
      proc.stop()


class TestUIStartup(unittest.TestCase):
  def test_c3x_settings_ready_before_layout_c4_unchanged(self):
    from openpilot.selfdrive.ui import ui
    for big in (True, False):
      calls = []
      with self.subTest(big=big), \
           mock.patch.object(ui, "BIG_UI", big), \
           mock.patch.object(ui, "config_realtime_process"), \
           mock.patch.object(ui.gui_app, "init_window"), \
           mock.patch.object(ui.gui_app, "render", return_value=iter(())), \
           mock.patch.object(ui.messaging, "PubMaster"), \
           mock.patch.object(ui.ui_state, "update_params", side_effect=lambda: calls.append("params")), \
           mock.patch.object(ui, "MainLayout", side_effect=lambda: calls.append("big")), \
           mock.patch.object(ui, "MiciMainLayout", side_effect=lambda: calls.append("mici")):
        ui.main()
      self.assertEqual(calls, ["params", "big"] if big else ["mici"])


if __name__ == "__main__":
  unittest.main(verbosity=2)
