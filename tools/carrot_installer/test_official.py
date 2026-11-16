import importlib.util
from pathlib import Path
import struct

import pytest

spec = importlib.util.spec_from_file_location('verify_official', Path(__file__).with_name('verify_official.py'))
official = importlib.util.module_from_spec(spec)
spec.loader.exec_module(official)


def elf(library=b'libdrm.so.2'):
  data = bytearray(1024)
  data[:6] = b'\x7fELF\x02\x01'
  struct.pack_into('<H', data, 18, 183)
  struct.pack_into('<Q', data, 32, 64)
  struct.pack_into('<HH', data, 54, 56, 2)
  struct.pack_into('<IIQQQQQQ', data, 64, 1, 4, 0, 0x400000, 0, 1024, 1024, 4096)
  struct.pack_into('<IIQQQQQQ', data, 120, 2, 4, 200, 0x400000 + 200, 0, 64, 64, 8)
  strings = b'\0' + library + b'\0'
  for pos, pair in enumerate([(5, 0x400000 + 300), (10, len(strings)), (1, 1), (0, 0)]):
    struct.pack_into('<qQ', data, 200 + 16 * pos, *pair)
  data[300:300 + len(strings)] = strings
  contract = b'/tmp/drmfd.sock\0git remote set-url origin\0carrot-wip?\0https://github.com/TonyBinheWu/openpilot.git?'
  data[500:500 + len(contract)] = contract
  return bytes(data)


def test_loader_dependencies_distinguish_wayland_from_drm():
  assert official.needed_libraries(elf()) == ['libdrm.so.2']
  assert official.validate(elf())['physical_C4_acceptance'] is False
  with pytest.raises(ValueError, match='legacy_wayland'):
    official.validate(elf(b'libwayland-client.so.0'))


def test_changed_target_or_cache_contract_is_rejected():
  for data in (elf().replace(b'TonyBinheWu', b'OtherPerson'),
               elf().replace(b'carrot-wip?', b'wrong-name?'),
               elf().replace(b'git remote set-url', b'git remote unknown')):
    with pytest.raises(ValueError):
      official.validate(data)


def test_bad_architecture_truncated_headers_and_segments_are_rejected():
  for data in (b'not ELF', elf()[:150], elf()[:900], elf()[:18] + b'\x3e\x00' + elf()[20:]):
    with pytest.raises(ValueError):
      official.validate(data)
