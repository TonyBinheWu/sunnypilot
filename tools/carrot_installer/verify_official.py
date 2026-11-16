"""Read-only verification of the official C4 installer; never execute it.

V1/v2's writable-cache tests did not exercise the embedded installer's display
backend. Check the actual downloaded ELF, its target and its loader dependencies.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import urllib.request

URL = 'https://installer.comma.ai/TonyBinheWu/carrot-wip'
MAX_BYTES = 8 * 1024 * 1024


def needed_libraries(data):
  if len(data) < 64 or data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', data, 18)[0] != 183:
    raise ValueError('expected_aarch64_elf64')
  offset = struct.unpack_from('<Q', data, 32)[0]
  size, count = struct.unpack_from('<HH', data, 54)
  if size != 56 or not 1 <= count <= 128 or offset + size * count > len(data):
    raise ValueError('invalid_program_headers')
  headers = [struct.unpack_from('<IIQQQQQQ', data, offset + i * size) for i in range(count)]
  entries = []
  for kind, _, file_offset, _, _, file_size, _, _ in headers:
    if file_offset + file_size > len(data):
      raise ValueError('truncated_segment')
    if kind == 2:
      if file_size % 16:
        raise ValueError('invalid_dynamic_segment')
      for pos in range(file_offset, file_offset + file_size, 16):
        tag, value = struct.unpack_from('<qQ', data, pos)
        if tag == 0:
          break
        entries.append((tag, value))
  needed = [value for tag, value in entries if tag == 1]
  if not needed:
    raise ValueError('dynamic_installer_expected')
  values = dict(entries)
  address, length = values.get(5), values.get(10)
  if address is None or length is None or length > MAX_BYTES:
    raise ValueError('missing_dynamic_strings')
  string_offset = next((file_offset + address - va for kind, _, file_offset, va, _, file_size, _, _ in headers
                        if kind == 1 and va <= address and address + length <= va + file_size), None)
  if string_offset is None:
    raise ValueError('invalid_dynamic_strings')
  table = data[string_offset:string_offset + length]
  result = []
  for pos in needed:
    end = table.find(b'\0', pos)
    if pos >= len(table) or end < 0:
      raise ValueError('invalid_library_name')
    result.append(table[pos:end].decode('ascii'))
  return result


def validate(data):
  if len(data) > MAX_BYTES:
    raise ValueError('installer_too_large')
  libraries = needed_libraries(data)
  if any('wayland' in name.lower() for name in libraries):
    raise ValueError('legacy_wayland_installer')
  for expected in (b'/tmp/drmfd.sock', b'git remote set-url origin', b'carrot-wip?'):
    if expected not in data:
      raise ValueError('installer_contract_changed')
  if not any(repo in data for repo in (b'https://github.com/TonyBinheWu/openpilot.git?',
                                      b'https://github.com/TonyBinheWu/sunnypilot.git?')):
    raise ValueError('wrong_repository')
  return {'url': URL, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
          'needed_libraries': libraries, 'display_contract': 'drmfd_socket_not_wayland',
          'branch': 'carrot-wip', 'physical_C4_acceptance': False}


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--output', required=True)
  args = parser.parse_args()
  reports = []
  for os_version in ('19.8', '20.0'):
    request = urllib.request.Request(URL, headers={'User-Agent': 'AGNOSSetup-' + os_version,
                                                 'X-openpilot-device-type': 'mici',
                                                 'X-openpilot-serial': 'TEST0000'})
    with urllib.request.urlopen(request, timeout=45) as response:
      report = validate(response.read(MAX_BYTES + 1))
    report['request_os_version'] = os_version
    reports.append(report)
  Path(args.output).write_text(json.dumps(reports, indent=2) + '\n', encoding='utf-8')
  print(json.dumps(reports, indent=2))


if __name__ == '__main__':
  main()
