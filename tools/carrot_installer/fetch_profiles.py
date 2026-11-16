"""Fetch immutable test/build inputs, verify bytes, never execute installers."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

UPSTREAM = 'https://i.carrotpilot.app/carrot-wip'
COMPAT = 'https://raw.githubusercontent.com/ajouatom/openpilot-installer-generator/df6f48de28e47afd6662e0a9184ac11d48733f26/agnos_compat/installer-agnos-19.6.3-carrot-base'
SOURCES = {
  'legacy': (UPSTREAM, '19.6.3', 'd0498d7da5458d2c963b2cda8419f6a3490c3a572e5c747d591e3fbde32148d9', 1270680),
  'current': (UPSTREAM, '19.8', 'ee2719d369d287b9f52d81dbd221ec16ab43d148da89d0b9bf2efe1bf52f20eb', 2051392),
  'compat': (COMPAT, '19.6.3-carrot', '85f6d9e54286a3842920d6967b187478b4e43d6171c331d72d3fb3102106e101', 1401224),
}


def main():
  parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True)
  root = Path(parser.parse_args().output); root.mkdir(parents=True, exist_ok=True)
  reports = {}
  for name, (url, version, sha, size) in SOURCES.items():
    request = urllib.request.Request(url, headers={'User-Agent': 'AGNOSSetup-' + version, 'X-openpilot-device-type': 'mici'})
    with urllib.request.urlopen(request, timeout=45) as response:
      data = response.read(2100001)
    if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
      raise ValueError('Upstream changed: inspect ' + name + ' before updating the pin')
    if data[:6] != b'\x7fELF\x02\x01' or int.from_bytes(data[18:20], 'little') != 183:
      raise ValueError('Wrong architecture')
    (root / (name + '.elf')).write_bytes(data)
    reports[name] = {'url': url, 'request_os': version, 'sha256': sha, 'bytes': size}
  (root / 'provenance.json').write_text(json.dumps(reports, indent=2) + '\n', encoding='utf-8')
  print(json.dumps(reports))


if __name__ == '__main__':
  main()
