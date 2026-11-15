#!/usr/bin/env python3
"""Check the device-facing notes before publishing either maintained branch."""
from datetime import date
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from openpilot.common.release_notes import read_release_notes


def check_release_notes(root: Path, expected_branch: str | None = None) -> None:
  version = (root / "openpilot/sunnypilot/common/version.h").read_text(encoding="utf-8").split('"')[1]
  text = (root / "CHANGELOG.md").read_text(encoding="utf-8-sig")
  notes = read_release_notes(str(root))
  match = re.fullmatch(r"sunnypilot (hkg-enhanced|ccnc-port) Version ([\d.]+) \((\d{4}-\d{2}-\d{2})\)", notes.splitlines()[0])
  if match is None or match[2] != version:
    raise ValueError("Latest CHANGELOG heading must name the maintained branch, version.h version and release date")
  if expected_branch in ("hkg-enhanced", "ccnc-port") and match[1] != expected_branch:
    raise ValueError("Release notes name a different branch than the update target")
  date.fromisoformat(match[3])
  if notes != text.split("\n\n", 1)[0].strip():
    raise ValueError("Keep the latest entry in one paragraph so older installed updaters can show every item")
  items = [line for line in notes.splitlines() if line.startswith("* ")]
  if not items or not all(re.search(r"[\u4e00-\u9fff]", item) for item in items):
    raise ValueError("Every update item must include a Traditional Chinese user-facing description")
  if not all(device in notes for device in ("C3X", "C4")):
    raise ValueError("Describe C3X and C4 changes or explicitly state that they are unchanged")


if __name__ == "__main__":
  check_release_notes(ROOT, os.environ.get("RELEASE_BRANCH"))
  print("Device release notes match the version and include Chinese C3X/C4 update items.")
