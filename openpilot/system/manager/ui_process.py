"""C3X-only UI crash capture and bounded offroad recovery."""
import os
import time
from pathlib import Path

from openpilot.common.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog
from openpilot.system.manager.process import PythonProcess, launcher
from openpilot.system.manager.ui_crash import capture_ui_crashes, record_event

RETRY_DELAYS = (2.0, 10.0, 30.0)


def crash_root() -> Path:
  return Path(Paths.crash_log_root()) / "c3x-ui"


def c3x_ui_launcher(module: str, name: str) -> None:
  with capture_ui_crashes(crash_root(), device="tizi", commit=os.environ.get("GIT_COMMIT", "unknown")):
    launcher(module, name)


class C3xUIProcess(PythonProcess):
  def __init__(self):
    super().__init__("ui", "openpilot.selfdrive.ui.ui", self._should_run)
    self.launcher = c3x_ui_launcher
    self._onroad = True  # fail closed until manager supplies its current state
    self._last_exit_pid = None
    self._retry_at = 0.0
    self._restarts = 0

  def _should_run(self, started, params, CP):
    self._onroad = bool(started)
    return True

  def start(self) -> None:
    if self.proc is not None and self.proc.exitcode is not None and not self.shutting_down:
      now = time.monotonic()
      if self.proc.pid != self._last_exit_pid:
        self._last_exit_pid = self.proc.pid
        delay = RETRY_DELAYS[min(self._restarts, len(RETRY_DELAYS) - 1)]
        self._retry_at = now + delay
        record_event(crash_root(), "ui_exit", pid=self.proc.pid, exitcode=self.proc.exitcode,
                     onroad=self._onroad, restarts=self._restarts)
        cloudlog.error(f"C3X UI exited with {self.proc.exitcode}; onroad={self._onroad}, restarts={self._restarts}")

      # Keep the dead process/exit code visible to managerState while onroad.
      # Never restart controls, change engagement, or retry indefinitely.
      if self._onroad or self._restarts >= len(RETRY_DELAYS) or now < self._retry_at:
        return

      self.stop()
      self._restarts += 1
      record_event(crash_root(), "ui_offroad_restart", attempt=self._restarts)

    super().start()


def make_ui_process(device_type: str) -> PythonProcess:
  if device_type == "tizi":
    return C3xUIProcess()
  return PythonProcess("ui", "openpilot.selfdrive.ui.ui", lambda started, params, CP: True)
