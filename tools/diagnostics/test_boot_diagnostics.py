"""Offline diagnostic fault injection. No car, CAN, model or GPU needed."""
import ast
import importlib.util
import json
import os
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "openpilot/system/manager/boot_diagnostics.py"
SCREEN = ROOT / "openpilot/system/ui/crash_screen.py"


def load(path):
  spec = importlib.util.spec_from_file_location(path.stem, path)
  assert spec is not None and spec.loader is not None
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


diag = load(GUARD)
screen = load(SCREEN)
TRACE = """Traceback (most recent call last):
  File "openpilot/selfdrive/ui/layouts/main.py", line 123, in render
    fail()
RuntimeError: injected UI failure
"""


class TestBootDiagnostics(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.env = patch.dict(os.environ, {"HKG_BOOT_DIAGNOSTICS": "1", "HKG_DIAGNOSTICS_ROOT": self.temp.name,
                                     "HKG_DIAGNOSTICS_SESSION": "session-test", "HKG_DIAGNOSTICS_NO_DISPLAY": "1"})
    self.env.start()
    self.addCleanup(self.env.stop)

  def run_guard(self, source, stage="manager"):
    result = subprocess.run([sys.executable, str(GUARD), stage, "--", sys.executable, "-c", source],
                            capture_output=True, timeout=15)
    path = Path(self.temp.name) / "latest-error.json"
    return result, json.loads(path.read_text()) if path.exists() else None

  def test_python_exception(self):
    result, report = self.run_guard("raise RuntimeError('injected startup error')")
    self.assertEqual(result.returncode, 1)
    self.assertIn("RuntimeError: injected startup error", report["summary"])
    self.assertIn(":1", report["location"])

  def test_import_failure_before_manager_main(self):
    _, report = self.run_guard("import nonexistent_hkg_diagnostic_test_module")
    self.assertIn("ModuleNotFoundError", report["summary"])

  def test_build_failure(self):
    result, report = self.run_guard("print('example.cc:17: error: injected compiler failure'); raise SystemExit(2)", "build")
    self.assertEqual(result.returncode, 2)
    self.assertIn("example.cc:17: error:", report["summary"])

  def test_successful_build_has_no_report(self):
    result, report = self.run_guard("print('build successful')", "build")
    self.assertEqual(result.returncode, 0)
    self.assertIsNone(report)

  def test_unexpected_zero_manager_exit_is_reported(self):
    _, report = self.run_guard("pass")
    self.assertEqual(report["exit"], "exit 0")

  def test_clean_shutdown_has_no_report(self):
    source = f"import runpy; m=runpy.run_path({str(GUARD)!r}); m['mark_clean_exit']()"
    result, report = self.run_guard(source)
    self.assertEqual(result.returncode, 0)
    self.assertIsNone(report)

  def test_stale_clean_marker_does_not_hide_new_failure(self):
    diag.mark_clean_exit()
    _, report = self.run_guard("pass")
    self.assertEqual(report["stage"], "manager")

  @unittest.skipUnless(sys.platform == "linux", "Linux signal semantics")
  def test_native_faults_are_recorded(self):
    for sig in (signal.SIGSEGV, signal.SIGABRT, signal.SIGKILL):
      with self.subTest(signal=sig.name):
        result, report = self.run_guard(f"import os,signal,resource; resource.setrlimit(resource.RLIMIT_CORE,(0,0)); os.kill(os.getpid(),{int(sig)})")
        self.assertEqual(result.returncode, 128 + sig)
        self.assertIn(sig.name, report["exit"])
        if sig != signal.SIGKILL:
          self.assertIn("Fatal Python error:", report["detail"])
        else:
          self.assertNotIn("OOM", report["summary"])

  def test_report_prefers_actual_exception_and_source(self):
    path = diag.report("ui", "startup environment: do not show\n" + TRACE, 1)
    report = json.loads(path.read_text())
    self.assertEqual(report["location"], "openpilot/selfdrive/ui/layouts/main.py:123")
    self.assertEqual(report["summary"], "RuntimeError: injected UI failure")
    self.assertNotIn("startup environment", report["detail"])

  def test_native_stack_uses_most_recent_first(self):
    path = diag.report("ui", 'Fatal Python error: Segmentation fault\nFile "inner.py", line 3\nFile "outer.py", line 8', -11)
    self.assertEqual(json.loads(path.read_text())["location"], "inner.py:3")

  def test_native_stack_selects_faulting_thread(self):
    trace = ('Fatal Python error: Segmentation fault\nThread 0x123 (most recent call first):\n'
             '  File "worker.py", line 10\nCurrent thread 0x456 (most recent call first):\n'
             '  File "fault.py", line 42\n  File "outer.py", line 8')
    report = json.loads(diag.report("ui", trace, -11).read_text())
    self.assertEqual(report["location"], "fault.py:42")

  def test_ui_crash_is_shown_once(self):
    proc = SimpleNamespace(pid=1234, exitcode=1)
    ui = SimpleNamespace(proc=proc, enabled=True, shutting_down=False)
    (diag.directory() / "ui-1234.trace").write_text(TRACE)
    monitor = diag.UiCrashMonitor()
    with patch.object(diag, "show") as show:
      show.return_value = None
      monitor.update(ui)
      monitor.update(ui)
      show.assert_called_once()
    report = json.loads((diag.directory() / "ui-error.json").read_text())
    self.assertIn("injected UI failure", report["summary"])

  def test_healthy_disabled_and_intentional_ui_stop_never_show(self):
    for proc, enabled, stopping in ((None, True, False), (SimpleNamespace(pid=12, exitcode=None), True, False),
                                    (SimpleNamespace(pid=12, exitcode=-2), True, True),
                                    (SimpleNamespace(pid=12, exitcode=1), False, False)):
      with self.subTest(proc=proc, enabled=enabled, stopping=stopping), patch.object(diag, "show") as show:
        diag.UiCrashMonitor().update(SimpleNamespace(proc=proc, enabled=enabled, shutting_down=stopping))
        show.assert_not_called()

  def test_disabled_diagnostics_have_no_io(self):
    with patch.dict(os.environ, {"HKG_BOOT_DIAGNOSTICS": "0"}), patch.object(diag, "directory") as directory:
      diag.UiCrashMonitor().update(None)
      diag.init_ui_capture()
      diag.mark_clean_exit()
      directory.assert_not_called()

  def test_storage_failure_does_not_raise_into_manager(self):
    with patch.object(diag, "directory", side_effect=OSError("read only")):
      diag.UiCrashMonitor().update(SimpleNamespace(proc=SimpleNamespace(pid=12, exitcode=1), enabled=True, shutting_down=False))
      self.assertIsNone(diag.report("ui", TRACE))

  def test_report_size_is_bounded(self):
    report = json.loads(diag.report("ui", "x" * 100000 + "\n" + TRACE).read_text())
    self.assertLessEqual(len(report["detail"]), diag.MAX_DETAIL)

  def test_log_rotation_is_bounded_and_preserves_exception(self):
    result, report = self.run_guard("print('x'*3000000); raise RuntimeError('tail survived')")
    self.assertEqual(result.returncode, 1)
    self.assertIn("tail survived", report["summary"])
    for path in diag.directory().glob("manager.log*"):
      self.assertLessEqual(path.stat().st_size, diag.MAX_LOG)
    self.assertEqual(len(list(diag.directory().glob("manager.log*"))), 2)

  @unittest.skipUnless(Path("/dev/full").exists(), "Requires Linux ENOSPC test device")
  def test_disk_full_flush_and_close_do_not_fail_successful_child(self):
    source = f"""import runpy, sys
from pathlib import Path
from unittest.mock import patch
m = runpy.run_path({str(GUARD)!r})
original = Path.open
def full_log(path, *args, **kwargs):
  if path.name == "build.log":
    return open("/dev/full", "wb")
  return original(path, *args, **kwargs)
with patch.object(Path, "open", full_log):
  raise SystemExit(m["run"]("build", [sys.executable, "-c", "print('force buffered flush')"]))
"""
    result = subprocess.run([sys.executable, "-c", source], capture_output=True, timeout=10)
    self.assertEqual(result.returncode, 0, result.stderr.decode())
    self.assertFalse((Path(self.temp.name) / "latest-error.json").exists())

  def test_retain_five_sessions_without_deleting_unowned_files(self):
    root = Path(self.temp.name)
    for i in range(9):
      path = root / f"session-{i}"
      path.mkdir()
      (path / ".boot-diagnostics-session").touch()
    unowned = root / "session-keep-user-files"
    unowned.mkdir()
    diag.retain_sessions(diag.directory())
    self.assertTrue(unowned.exists())
    self.assertEqual(len(list(root.glob("session-*/.boot-diagnostics-session"))), 5)

  def test_terminal_controls_and_common_secrets_are_removed(self):
    text = diag.sanitize("\x1b[31mRuntimeError: password=abc token=def Bearer xyz\x00")
    for secret in ("abc", "def", "xyz", "\x1b", "\x00"):
      self.assertNotIn(secret, text)

  def test_ui_fatal_capture_survives_native_abort(self):
    source = f"import runpy, os, signal, resource; m=runpy.run_path({str(GUARD)!r}); "
    source += "resource.setrlimit(resource.RLIMIT_CORE,(0,0)); m['init_ui_capture'](); os.kill(os.getpid(),signal.SIGABRT)"
    result = subprocess.run([sys.executable, "-c", source], capture_output=True, timeout=5)
    self.assertEqual(result.returncode, -signal.SIGABRT)
    trace = next(diag.directory().glob("ui-*.trace")).read_text()
    self.assertIn("Fatal Python error", trace)

  @unittest.skipUnless(sys.platform == "linux", "Linux processes")
  def test_live_ui_guard_and_stale_pid(self):
    diag.atomic_json(diag.directory() / "ui-process.json", {"pid": os.getpid()})
    self.assertTrue(diag.ui_is_alive())
    diag.atomic_json(diag.directory() / "ui-process.json", {"pid": 999999999})
    self.assertFalse(diag.ui_is_alive())

  def test_sigterm_forwarding_is_not_reported_as_crash(self):
    guard = subprocess.Popen([sys.executable, str(GUARD), "manager", "--", sys.executable, "-c", "import time; print('READY',flush=True); time.sleep(30)"],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
      self.assertEqual(guard.stdout.readline().strip(), b"READY")
      guard.terminate()
      guard.communicate(timeout=5)
      self.assertFalse((Path(self.temp.name) / "latest-error.json").exists())
    finally:
      if guard.poll() is None:
        guard.kill()
        guard.communicate(timeout=5)

  def test_long_paths_and_messages_fit_both_layouts(self):
    data = {"stage": "ui", "exit": "exit 1", "location": "/" + "long/path/" * 40 + "main.py:123", "summary": "RuntimeError: " + "X" * 400,
            "detail": TRACE * 30}
    for device in ("tizi", "mici"):
      with self.subTest(device=device):
        self.assertEqual(screen.screen_size(device), (2160, 1080) if device == "tizi" else (536, 240))
        pages = screen.pages(data, columns=35)
        self.assertGreater(len(pages), 1)
        self.assertIn("main.py:123", "\n".join(pages[0]))
        self.assertIn("RuntimeError", "\n".join(pages[0]))
        for page in pages:
          self.assertLessEqual(len(page), 7)
          self.assertTrue(all(len(line) <= 35 for line in page))

  def test_screen_has_no_main_ui_or_built_dependency_imports(self):
    tree = ast.parse(SCREEN.read_text())
    modules = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    self.assertFalse(any(name.startswith("openpilot") for name in modules if name))

  def test_production_hooks_are_present(self):
    process = (ROOT / "openpilot/system/manager/process.py").read_text()
    manager = (ROOT / "openpilot/system/manager/manager.py").read_text()
    launch = (ROOT / "launch_chffrplus.sh").read_text()
    self.assertLess(process.index("    init_ui_capture()"), process.index("    mod = importlib.import_module(proc)"))
    self.assertIn("save_ui_exception(traceback.format_exc())", process)
    self.assertIn('ui_crash_monitor.update(managed_processes["ui"])', manager)
    self.assertIn("    mark_clean_exit()", manager)
    self.assertIn("guarded_start manager ./manager.py", launch)
    self.assertIn("guarded_start build ./build.py ||", launch)


if __name__ == "__main__":
  unittest.main(verbosity=2)
