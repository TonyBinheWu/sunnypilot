"""Read Formosa user-data SEI without decoding or changing video pixels."""
import io
import json
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


def metadata_from_nals(units, codec):
  for nal in units:
    if len(nal) < 2 or ((nal[0] >> 1) & 63 not in (39, 40) if codec == 'hevc' else nal[0] & 31 != 6):
      continue
    rbsp = bytearray()
    zeros = 0
    for byte in nal[2 if codec == 'hevc' else 1:]:
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
          break
        value += rbsp[at]
        at += 1
        values.append(value)
      if len(values) != 2:
        break
      kind, size = values
      payload = rbsp[at:at + size]
      if len(payload) != size:
        break
      at += size
      if kind == 5 and 16 <= size <= 2064 and payload[:16] == UUID:
        try:
          item = json.loads(payload[16:], parse_constant=lambda _: None)
          if isinstance(item, dict) and item.get('schema') == 'formosa.drive.v1':
            yield item
        except (ValueError, UnicodeError):
          continue


def driving_metadata(stream, codec):
  yield from metadata_from_nals(nals(stream), codec)


def packet_metadata(data, codec, length_size=0):
  """Demuxed MP4 packets use the avcC/hvcC length size, TS uses Annex B."""
  if not length_size:
    yield from driving_metadata(io.BytesIO(data), codec)
    return
  if length_size not in (1, 2, 3, 4):
    return
  units = []
  at = 0
  while at + length_size <= len(data):
    size = int.from_bytes(data[at:at + length_size], 'big')
    at += length_size
    if not size or at + size > len(data):
      return
    units.append(data[at:at + size])
    at += size
  if at == len(data):
    yield from metadata_from_nals(units, codec)
