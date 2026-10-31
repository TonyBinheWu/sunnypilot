"""Persistent C3X UI diagnostics; exceptions and fatal signals remain fatal."""
import faulthandler
import json
import os
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from pathlib import Path

MAX_TRACEBACK_BYTES = 65536


def record_event(root: Path, event: str, **fields) -> None:
  """Best-effort, bounded supervisor history; never raises into manager."""
  try:
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = root / "events.jsonl"
    if path.exists() and path.stat().st_size > MAX_TRACEBACK_BYTES:
      path.replace(root / "events.jsonl.1")
    line = json.dumps({"time": time.time(), "event": event, **fields}) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as f:
      f.write(line)
  except OSError as exc:
    print(f"UI diagnostic event unavailable: {exc}", file=sys.stderr)


@contextmanager
def capture_ui_crashes(root: Path, **metadata):
  """Keep the last three UI launches, including Python and native crash stacks."""
  stream = None
  old_thread_hook = threading.excepthook
  fault_handler_was_enabled = faulthandler.is_enabled()
  fault_handler_installed = False
  thread_errors = 0
  lock = threading.Lock()

  def write(text: str) -> None:
    if stream is not None:
      try:
        with lock:
          stream.write(text.encode("utf-8", errors="replace")[-MAX_TRACEBACK_BYTES:])
      except (OSError, ValueError):
        pass

  def thread_hook(args):
    nonlocal thread_errors
    thread_errors += 1
    if thread_errors <= 8:
      write(f"\nTHREAD EXCEPTION: {args.thread.name if args.thread else 'unknown'}\n")
      write("".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)))
    old_thread_hook(args)

  try:
    try:
      root.mkdir(parents=True, exist_ok=True, mode=0o700)
      previous = root / "ui.log.1"
      if previous.exists():
        previous.replace(root / "ui.log.2")
      current = root / "ui.log"
      if current.exists():
        current.replace(previous)
      fd = os.open(current, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
      stream = os.fdopen(fd, "wb", buffering=0)
      write(json.dumps({"time": time.time(), "pid": os.getpid(), **metadata}) + "\n")
      faulthandler.enable(file=stream, all_threads=True)
      fault_handler_installed = True
      threading.excepthook = thread_hook
    except OSError as exc:
      print(f"UI crash capture unavailable: {exc}", file=sys.stderr)

    try:
      yield
    except BaseException as exc:
      write("\nUI EXCEPTION\n" + "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
      raise
    else:
      write("\nUI launcher returned normally\n")
  finally:
    threading.excepthook = old_thread_hook
    if fault_handler_installed:
      faulthandler.disable()
      if fault_handler_was_enabled:
        faulthandler.enable()
    if stream is not None:
      stream.close()
