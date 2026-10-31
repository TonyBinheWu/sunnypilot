"""Collect a private, read-only crash report. Does not start or stop any service."""
import argparse
import datetime
import os
import subprocess
from pathlib import Path

LIMIT = 65536


def tail(path: Path) -> str:
  try:
    with path.open("rb") as f:
      f.seek(0, os.SEEK_END)
      f.seek(max(0, f.tell() - LIMIT))
      return f.read(LIMIT).decode("utf-8", errors="replace")
  except OSError as exc:
    return f"unavailable: {exc}\n"


def command(args: list[str]) -> str:
  try:
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=8, check=False)
    return f"exit={result.returncode}\n" + result.stdout[-LIMIT:].decode("utf-8", errors="replace")
  except (OSError, subprocess.TimeoutExpired) as exc:
    return f"unavailable: {exc}\n"


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--output", type=Path)
  args = parser.parse_args()
  now = datetime.datetime.now(datetime.timezone.utc)
  stamp = now.strftime("%Y%m%dT%H%M%SZ")
  root = Path("/data/community/crashes")
  output = args.output or root / f"c3x-ui-report-{stamp}-{os.getpid()}.txt"
  repo = Path(__file__).resolve().parents[2]
  output.parent.mkdir(parents=True, exist_ok=True)
  fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
  with os.fdopen(fd, "w", encoding="utf-8") as report:
    report.write(f"C3X UI diagnostics | UTC {now.isoformat()}\n")
    report.write("PRIVATE: logs may contain device identifiers and network information. Review before sharing.\n")
    report.write("No parameters changed; no services started, stopped or restarted.\n")
    commands = [
      ["git", "-C", str(repo), "log", "-1", "--format=%H %s"],
      ["git", "-C", str(repo), "status", "--short"],
      ["uname", "-a"], ["uptime"], ["df", "-h", "/data"],
      ["ps", "-eo", "pid,ppid,stat,comm"],
      ["tmux", "capture-pane", "-p", "-S", "-200"],
      ["dmesg", "--ctime", "--color=never"],
      ["journalctl", "-b", "-n", "150", "--no-pager", "-o", "short-monotonic"],
      ["journalctl", "-k", "-b", "-1", "-n", "100", "--no-pager"],
    ]
    for args in commands:
      report.write("\n=== " + " ".join(args) + " ===\n" + command(args))
    paths = [Path("/VERSION"), Path("/proc/meminfo"), Path("/tmp/tmux_error.log")]
    paths += [Path("/data/params/d") / key for key in ("GitCommit", "GitBranch", "IsOffroad", "LastManagerExitReason")]
    paths += [root / "c3x-ui" / name for name in ("ui.log", "ui.log.1", "ui.log.2", "events.jsonl", "events.jsonl.1")]
    try:
      paths += sorted(Path("/sys/fs/pstore").glob("*"))[:6]
    except OSError:
      pass
    for path in paths:
      report.write(f"\n=== {path} ===\n" + tail(path))
  print(f"Report saved: {output}")
  print("This report stays on this device; it was not uploaded.")


if __name__ == "__main__":
  main()
