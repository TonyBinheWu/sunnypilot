#!/usr/bin/env python3
"""Read Formosa driving metadata from an Annex-B H.264/H.265 video. No network."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from openpilot.system.loggerd.driving_metadata import UUID, START, nals, driving_metadata  # noqa: E402,F401


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('video', type=Path)
  parser.add_argument('--codec', choices=('hevc', 'h264'), default='hevc')
  args = parser.parse_args()
  with args.video.open('rb') as stream:
    for metadata in driving_metadata(stream, args.codec):
      print(json.dumps(metadata, ensure_ascii=False, allow_nan=False))
