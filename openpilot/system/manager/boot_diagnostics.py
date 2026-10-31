"""Best-effort, stdlib-only crash reports. Never restart driving processes."""
import argparse
import faulthandler
import json
import os
import re
import selectors
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAX_LOG = 1024 * 1024
MAX_DETAIL = 32768
_fault_file = None


def enabled() -> bool:
  return os.getenv("HKG_BOOT_DIAGNOSTICS") == "1"


def directory() -> Path:
  session = re.sub(r"[^a-zA-Z0-9_-]", "_", os.getenv("HKG_DIAGNOSTICS_SESSION", f"manual-{os.getpid()}"))[:80]
  for base in (Path(os.getenv("HKG_DIAGNOSTICS_ROOT", "/data/diagnostics/hkg")), Path("/tmp/hkg-diagnostics")):
    try:
      path = base / session
      path.mkdir(parents=True, exist_ok=True, mode=0o700)
      return path
    except OSError:
      continue
  raise OSError("No writable diagnostic directory")


def retain_sessions(path: Path) -> None:
  """Keep five boots; only remove directories explicitly created by this guard."""
  try:
    (path / ".boot-diagnostics-session").touch()
    old = sorted((p for p in path.parent.glob("session-*")
                  if p != path and not p.is_symlink() and (p / ".boot-diagnostics-session").is_file()),
                 key=lambda p: p.stat().st_mtime, reverse=True)
    for previous in old[4:]:
      shutil.rmtree(previous)
  except OSError:
    pass


def tail(path: Path, limit: int = MAX_DETAIL) -> str:
  try:
    with path.open("rb") as f:
      f.seek(0, 2)
      f.seek(max(0, f.tell() - limit))
      return f.read(limit).decode("utf-8", "replace")
  except OSError:
    return ""


def atomic_json(path: Path, data: dict) -> None:
  temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
  try:
    with temporary.open("w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=2)
      f.flush()
      os.fsync(f.fileno())
    temporary.replace(path)
  finally:
    temporary.unlink(missing_ok=True)


def device_type() -> str:
  model = tail(Path("/sys/firmware/devicetree/base/model"), 256).strip("\x00\n ")
  return model.split("comma ")[-1] if model else "pc"


def version() -> str:
  try:
    return subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT,
                                   stderr=subprocess.DEVNULL, timeout=1).decode().strip()
  except (OSError, subprocess.SubprocessError):
    return "unknown"


def sanitize(text: str) -> str:
  text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
  text = re.sub(r"(?i)(bearer\s+)\S+", r"\1[redacted]", text)
  text = re.sub(r"(?i)((?:token|password|secret|api_key)\s*[:=]\s*)\S+", r"\1[redacted]", text)
  return "".join(c for c in text if c in "\n\t" or c.isprintable())


def describe_exit(code: int | None) -> str:
  if code is None:
    return "exception"
  if code < 0:
    try:
      return f"exit {code} ({signal.Signals(-code).name})"
    except ValueError:
      pass
  return f"exit {code}"


def report(stage: str, detail: str, code: int | None = None) -> Path | None:
  """Record before rendering; a broken display must not destroy evidence."""
  try:
    path = directory()
    detail = sanitize(detail[-MAX_DETAIL:])
    # Only show the traceback, not preceding environment/registration log lines.
    starts = [detail.rfind("Traceback (most recent call last):"), detail.rfind("Fatal Python error:")]
    if max(starts) >= 0:
      detail = detail[max(starts):]
    stack = detail
    if "Fatal Python error:" in detail:
      # all_threads dumps can list a waiting thread before the faulting thread.
      current = re.search(r"^Current thread .*:$", detail, re.MULTILINE)
      if current is not None:
        stack = detail[current.start():]
    frames = re.findall(r'File "([^"]+)", line (\d+)', stack)
    frame = (frames[0] if "Fatal Python error:" in detail else frames[-1]) if frames else None
    location = f"{frame[0].replace(str(ROOT) + '/', '')}:{frame[1]}" if frame else "No Python frame recorded"
    errors = [line.strip() for line in detail.splitlines()
              if re.match(r"(?:[\w.]+(?:Error|Exception)|Fatal Python error|SystemExit|KeyboardInterrupt)\b", line.strip())]
    if not errors:
      errors = [line.strip() for line in detail.splitlines() if "error:" in line.lower() or "scons: ***" in line]
    summary = errors[-1] if errors else f"{stage} stopped: {describe_exit(code)}; see saved log"
    data = {"id": f"{time.time_ns():x}", "time": time.strftime("%Y-%m-%d %H:%M:%S %z"),
            "device": device_type(), "commit": version(), "stage": stage, "exit": describe_exit(code),
            "summary": summary[:512], "location": location, "detail": detail, "directory": str(path)}
    result = path / f"{stage}-error.json"
    atomic_json(result, data)
    atomic_json(path / "latest-error.json", data)
    atomic_json(path.parent / "latest-error.json", data)
    print(f"HKG DIAGNOSTIC: {summary}\n{location}\nReport: {result}", flush=True)
    return result
  except Exception as e:
    print(f"Cannot save diagnostic: {e}", file=sys.stderr, flush=True)
    return None


def init_ui_capture() -> None:
  global _fault_file
  if not enabled():
    return
  try:
    path = directory()
    _fault_file = (path / f"ui-{os.getpid()}.trace").open("w", encoding="utf-8", buffering=1)
    faulthandler.enable(file=_fault_file, all_threads=True)
    atomic_json(path / "ui-process.json", {"pid": os.getpid()})
  except Exception:
    pass  # Diagnostics must not prevent the normal UI from starting.


def save_ui_exception(detail: str) -> None:
  if _fault_file is not None:
    try:
      _fault_file.write(detail[-MAX_DETAIL:])
      _fault_file.flush()
      os.fsync(_fault_file.fileno())
    except OSError:
      pass


def ui_is_alive() -> bool:
  try:
    pid = int(json.loads((directory() / "ui-process.json").read_text())["pid"])
    # A zombie has exited and no longer owns the display.
    state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    return state != "Z"
  except (OSError, ValueError, KeyError, IndexError):
    return False


def show(path: Path | None) -> subprocess.Popen | None:
  if path is None or os.getenv("HKG_DIAGNOSTICS_NO_DISPLAY") == "1":
    return None
  try:
    with (path.parent / "display.log").open("w") as log:
      return subprocess.Popen([sys.executable, str(ROOT / "openpilot/system/ui/crash_screen.py"), str(path)],
                              stdout=log, stderr=subprocess.STDOUT, close_fds=True)
  except OSError as e:
    print(f"Diagnostic display failed: {e}", file=sys.stderr, flush=True)
    return None


class UiCrashMonitor:
  """Observe actual UI exit only. Do not kill, time out, or restart a live UI."""
  def __init__(self):
    self.pid: int | None = None
    self.display: subprocess.Popen | None = None

  def update(self, ui) -> None:
    if not enabled():
      return
    try:
      proc = ui.proc
      if proc is None or ui.shutting_down or not ui.enabled:
        self.close()
        return
      if proc.exitcode is None:
        self.close()
        return
      if self.pid == proc.pid:
        return
      self.close()
      self.pid = proc.pid
      path = report("ui", tail(directory() / f"ui-{proc.pid}.trace"), proc.exitcode)
      self.display = show(path)
    except Exception as e:
      print(f"UI diagnostic unavailable: {e}", file=sys.stderr, flush=True)

  def close(self) -> None:
    if self.display is not None:
      try:
        self.display.terminate()
        try:
          self.display.wait(timeout=1)
        except subprocess.TimeoutExpired:
          self.display.kill()
          self.display.wait(timeout=1)
      except (OSError, subprocess.TimeoutExpired):
        pass
      self.display = None
    self.pid = None


def mark_clean_exit() -> None:
  if enabled():
    try:
      (directory() / "manager-clean-exit").touch()
    except OSError:
      pass


def close_log(log) -> None:
  # Buffered close can repeat a failed flush (e.g. ENOSPC). Never fail the guard.
  if log is not None:
    try:
      log.close()
    except OSError:
      pass


def run(stage: str, command: list[str]) -> int:
  """Capture imports, signals and child output without importing built modules."""
  log = None
  try:
    path = directory()
    retain_sessions(path)
    log_path = path / f"{stage}.log"
    log = log_path.open("wb")
    if stage == "manager":
      (path / "manager-clean-exit").unlink(missing_ok=True)
  except OSError:
    close_log(log)
    return subprocess.call(command)  # Storage failure must not prevent startup.

  interrupted = False
  child = None

  def forward(signum, _frame):
    nonlocal interrupted
    interrupted = True
    if child is not None and child.poll() is None:
      try:
        child.send_signal(signum)
      except ProcessLookupError:
        pass

  handlers = {sig: signal.signal(sig, forward) for sig in (signal.SIGTERM, signal.SIGINT)}
  try:
    child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONFAULTHANDLER": "1"})
    assert child.stdout is not None
    with selectors.DefaultSelector() as selector:
      selector.register(child.stdout, selectors.EVENT_READ)
      exited_at = None
      while True:
        if child.poll() is not None:
          exited_at = exited_at or time.monotonic()
          if time.monotonic() - exited_at > 1:
            break  # Surviving descendants may still hold the pipe open.
        events = selector.select(0.1)
        if not events:
          continue
        data = os.read(child.stdout.fileno(), 16384)
        if not data:
          break
        try:
          sys.stdout.buffer.write(data)
          sys.stdout.buffer.flush()
        except OSError:
          pass
        try:
          if log is not None:
            if log.tell() + len(data) > MAX_LOG:
              close_log(log)
              log = None
              log_path.replace(log_path.with_suffix(".log.1"))
              log = log_path.open("wb")
            log.write(data)
            log.flush()
        except OSError:
          close_log(log)
          log = None  # Disk full/read-only must not terminate the child.
    code = child.wait()
    child.stdout.close()
  except OSError as e:
    code = 127
    try:
      if log is not None:
        log.write(f"{type(e).__name__}: {e}\n".encode())
    except OSError:
      pass
  finally:
    close_log(log)
    for sig, handler in handlers.items():
      signal.signal(sig, handler)

  clean = stage == "manager" and (path / "manager-clean-exit").exists()
  failed = code != 0 or (stage == "manager" and not clean)
  if failed and not interrupted:
    diagnostic = report(stage, tail(log_path.with_suffix(".log.1")) + tail(log_path), code)
    # SIGKILL of manager can leave a functioning UI alive. Do not cover it.
    display = None if ui_is_alive() else show(diagnostic)
    if display is not None:
      display.wait()  # No auto-dismiss/reboot; the user can photograph the error.
  return code if code >= 0 else 128 - code


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("stage", choices=("build", "manager"))
  parser.add_argument("command", nargs=argparse.REMAINDER)
  args = parser.parse_args()
  command = args.command[1:] if args.command[:1] == ["--"] else args.command
  if not command:
    parser.error("a command is required")
  raise SystemExit(run(args.stage, command))


if __name__ == "__main__":
  main()
