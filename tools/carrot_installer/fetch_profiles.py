"""Fetch immutable test/build inputs, verify bytes, never execute installers."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

UPSTREAM = 'https://i.carrotpilot.app/carrot-wip'
CLASSIC_UPSTREAM = 'https://install.sunnypilot.ai/fork/TonyBinheWu/carrot-wip'
COMPAT = 'https://raw.githubusercontent.com/ajouatom/openpilot-installer-generator/df6f48de28e47afd6662e0a9184ac11d48733f26/agnos_compat/installer-agnos-19.6.3-carrot-base'
SOURCES = {
  'classic': (CLASSIC_UPSTREAM, '', 'c8391b7db3bb62af86e71c3aad325815fa736e3ba6e763c1aac5279b8c15ed3e', 1295328),
  'carrotBt1': (UPSTREAM, '19.8-carrot-bt1', '972678b20da245a1a1f68835b3705233e4ded63077ca610e45ed6bcf242d1fd0', 1401224),
  'legacy': (UPSTREAM, '19.6.3', 'd0498d7da5458d2c963b2cda8419f6a3490c3a572e5c747d591e3fbde32148d9', 1270680),
  'current': (UPSTREAM, '19.8', 'ee2719d369d287b9f52d81dbd221ec16ab43d148da89d0b9bf2efe1bf52f20eb', 2051392),
  'compat': (COMPAT, '19.6.3-carrot', '85f6d9e54286a3842920d6967b187478b4e43d6171c331d72d3fb3102106e101', 1401224),
}
MATRIX = {
  'tici': {'':'classic','12.8':'legacy','19.6.3':'current','19.6.3-carrot':'current','19.8':'current','20.0':'current','19.8-carrot-bt1':'carrotBt1'},
  'tizi': {'':'classic','12.8':'legacy','19.6.3':'legacy','19.6.3-carrot':'legacy','19.8':'current','20.0':'current','19.8-carrot-bt1':'carrotBt1'},
  'mici': {'19.6.3':'legacy','19.8':'current','20.0':'current','19.8-carrot-bt1':'carrotBt1'},
}


def fetch(url, version, device, sha, size):
  request = urllib.request.Request(url, headers={'User-Agent': 'AGNOSSetup' + ('-' + version if version else ''), 'X-openpilot-device-type': device})
  with urllib.request.urlopen(request, timeout=45) as response:
    data = response.read(2100001)
  if len(data) != size or hashlib.sha256(data).hexdigest() != sha:
    raise ValueError('Upstream changed: inspect ' + device + '/' + version + ' before updating the pin')
  if data[:6] != b'\x7fELF\x02\x01' or int.from_bytes(data[18:20], 'little') != 183:
    raise ValueError('Wrong architecture')
  return data


def main():
  parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True)
  root = Path(parser.parse_args().output); root.mkdir(parents=True, exist_ok=True)
  reports = {}
  for name, (url, version, sha, size) in SOURCES.items():
    device = 'tici' if name == 'classic' else 'mici'
    data = fetch(url, version, device, sha, size)
    (root / (name + '.elf')).write_bytes(data)
    reports[name] = {'url': url, 'request_os': version, 'device': device, 'sha256': sha, 'bytes': size}
    print('Verified profile: ' + name, flush=True)
  matrix = []
  for device, versions in MATRIX.items():
    for version, profile in versions.items():
      _, _, sha, size = SOURCES[profile]
      fetch(CLASSIC_UPSTREAM if not version else UPSTREAM, version, device, sha, size)
      matrix.append({'device': device, 'version': version, 'profile': profile, 'sha256': sha})
    print('Verified routing: ' + device, flush=True)
  (root / 'routing-matrix.json').write_text(json.dumps(matrix, indent=2) + '\n', encoding='utf-8')
  (root / 'provenance.json').write_text(json.dumps(reports, indent=2) + '\n', encoding='utf-8')
  print(json.dumps(reports))


if __name__ == '__main__':
  main()
