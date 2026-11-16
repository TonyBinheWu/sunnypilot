"""Build a static C4 compatibility entry around an immutable upstream installer.

Never execute the downloaded payload on the build host. Reject changed bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import urllib.request

URL='https://install.sunnypilot.ai/fork/TonyBinheWu/carrot-wip'
SHA256='6dd19d20101586b49e5322cf9b3070380cd97e7abd34c6c51f325ffb5fa49a4b'


def validate(data):
  if hashlib.sha256(data).hexdigest()!=SHA256:
    raise ValueError('Upstream installer changed; inspect before updating the pin')
  if data[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(data[18:20],'little')!=183:
    raise ValueError('Expected little-endian ELF64 aarch64')
  for value in (b'TonyBinheWu/openpilot.git?', b'carrot-wip?', b'libwayland-client.so.0'):
    if value not in data:raise ValueError('Unexpected installer configuration')
  return data


def main():
  parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--cc',default='gcc')
  args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
  request=urllib.request.Request(URL,headers={'User-Agent':'AGNOSSetup','X-openpilot-device-type':'mici'})
  with urllib.request.urlopen(request,timeout=60) as response:data=validate(response.read(2_000_001))
  with tempfile.TemporaryDirectory() as temp:
    source=Path(temp)/'payload.c'
    source.write_text('#include <stddef.h>\nconst unsigned char installer_payload[]={'+','.join(map(str,data))+'};\nconst size_t installer_size=sizeof(installer_payload);\n')
    binary=out/'carrot-c4-installer'
    subprocess.run([args.cc,'-std=c11','-O2','-Wall','-Wextra','-Werror','-static',str(Path(__file__).with_name('bootstrap.c')),str(source),'-o',str(binary)],check=True)
  result=binary.read_bytes()
  if result[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(result[18:20],'little')!=183:raise ValueError('Wrong build architecture')
  manifest={'version':2,'device':'mici/C4','repository':'https://github.com/TonyBinheWu/sunnypilot.git','branch':'carrot-wip',
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'upstream_url':URL,'upstream_device_header':'mici','upstream_sha256':SHA256,
            'sha256':hashlib.sha256(result).hexdigest(),'bytes':len(result)}
  (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print(json.dumps(manifest))


if __name__=='__main__':main()
