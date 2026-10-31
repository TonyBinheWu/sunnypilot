#!/usr/bin/env python3
import argparse
import hashlib
import math
import os
import subprocess

# This licensed CJK font is deliberately stored outside LFS so device updates
# always include it. Keep the exception limited to the reviewed file contents.
BUNDLED_FONT = "openpilot/selfdrive/assets/fonts/SourceHanSansTC-Regular.otf"
BUNDLED_FONT_SHA256 = "10e6d832bc73650840aa7fbfec4e10c527f8136ae2aec71c3e1c13a67475c24a"


def lfs_files(filenames: list[str]) -> set[str]:
  if not filenames:
    return set()

  result = subprocess.run(
    ("git", "check-attr", "filter", "-z", "--stdin"),
    input="\0".join(filenames),
    check=True,
    capture_output=True,
    text=True,
  )
  fields = result.stdout.rstrip("\0").split("\0") if result.stdout else []
  return {fields[i] for i in range(0, len(fields), 3) if fields[i + 2] == "lfs"}


def check_added_large_files(filenames: list[str], max_kb: int) -> int:
  failed = False
  ignored = lfs_files(filenames)
  for filename in filenames:
    if filename == BUNDLED_FONT:
      with open(filename, "rb") as font:
        if hashlib.file_digest(font, "sha256").hexdigest() != BUNDLED_FONT_SHA256:
          print(f"{filename}: bundled font checksum changed; review its source and license.")
          failed = True
      continue
    if filename in ignored:
      continue

    size_kb = math.ceil(os.stat(filename).st_size / 1024)
    if size_kb > max_kb:
      print(f"{filename} ({size_kb} KB) exceeds {max_kb} KB.")
      failed = True

  return int(failed)


def main() -> int:
  parser = argparse.ArgumentParser(description="Check that tracked files do not exceed a size limit.")
  parser.add_argument("filenames", nargs="*")
  parser.add_argument("--maxkb", type=int, default=500, help="maximum allowable size in KiB")
  args = parser.parse_args()
  return check_added_large_files(args.filenames, args.maxkb)


if __name__ == "__main__":
  raise SystemExit(main())
