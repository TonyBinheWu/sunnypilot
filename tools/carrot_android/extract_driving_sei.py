#!/usr/bin/env python3
"""Read Formosa driving metadata from an Annex-B H.264/H.265 video. No network."""
import argparse
import json
from pathlib import Path
import re

UUID = bytes.fromhex('d15fb7ea55694bdfa6404f524d4f5341')
START = re.compile(b'\x00\x00(?:\x00)?\x01')


def nals(stream):
  pending = b''
  while True:
    chunk = stream.read(256 * 1024)
    pending += chunk
    matches = list(START.finditer(pending))
    for first, second in zip(matches, matches[1:]):
      yield pending[first.end():second.start()]
    if matches:
      pending = pending[matches[-1].start():]
    if not chunk:
      last = START.match(pending)
      if last:
        yield pending[last.end():]
      return
    if len(pending) > 32 * 1024 * 1024:
      raise ValueError('NAL exceeds 32 MiB; check the raw video format')


def driving_metadata(stream, codec):
  for nal in nals(stream):
    if len(nal) < 2 or ((nal[0] >> 1) & 63 not in (39, 40) if codec == 'hevc' else nal[0] & 31 != 6):
      continue
    escaped = nal[2 if codec == 'hevc' else 1:]
    rbsp = bytearray()
    zeros = 0
    for byte in escaped:
      if zeros == 2 and byte == 3:
        zeros = 0
        continue
      rbsp.append(byte)
      zeros = zeros + 1 if byte == 0 else 0
    at = 0
    while at < len(rbsp) and rbsp[at] != 0x80:
      values = []
      for _ in range(2):
        value = 0
        while at < len(rbsp) and rbsp[at] == 255:
          value += 255
          at += 1
        if at >= len(rbsp):
          return
        value += rbsp[at]
        at += 1
        values.append(value)
      kind, size = values
      payload = rbsp[at:at + size]
      if len(payload) != size:
        break
      at += size
      if kind == 5 and 16 <= size <= 2064 and payload[:16] == UUID:
        try:
          item = json.loads(payload[16:])
          if isinstance(item, dict) and item.get('schema') == 'formosa.drive.v1':
            yield item
        except (ValueError, UnicodeError):
          continue


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('video', type=Path)
  parser.add_argument('--codec', choices=('hevc', 'h264'), default='hevc')
  args = parser.parse_args()
  with args.video.open('rb') as stream:
    for metadata in driving_metadata(stream, args.codec):
      print(json.dumps(metadata, ensure_ascii=False, allow_nan=False))
