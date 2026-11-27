"""Build the fixed-size ARM kernel offline; install only the byte-verified result."""
import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import torch
from torch.nn.functional import interpolate

from . import OBJECT_NAME, OBJECT_SHA256

SOURCE = Path(__file__).resolve().parent
X_SHA256 = '55bd982cec453547c7c27831898b88e0253ce981cee7336fbf74527dee082847'
Y_SHA256 = 'd5d09a293e1983b766b56d6dcddb9e571024826fdf7a91dcbbf94301d5ed16d9'


def axis(size, out, dim, digest):
  # Independent unit impulses recover the normalized float32 weights, including clipped borders.
  shape = (size, out) if dim == 'x' else (out, size)
  identity = torch.eye(size, dtype=torch.float32, device='cpu')[None, None]
  response = interpolate(identity, shape, mode='bicubic', align_corners=False, antialias=True)[0, 0]
  matrix = (response.T if dim == 'x' else response).contiguous().numpy()
  if hashlib.sha256(matrix).hexdigest() != digest:
    raise ValueError(f'Unexpected Torch interpolation coefficients on {dim} axis')
  starts = np.zeros(out, dtype=np.int16)
  counts = np.zeros(out, dtype=np.uint8)
  weights = np.zeros((out, 6), dtype=np.float32)
  for i, row in enumerate(matrix):
    indices = np.flatnonzero(row)
    lo, end = indices[0], indices[-1]+1
    starts[i], counts[i] = lo, end-lo
    weights[i, :end-lo] = row[lo:end]
  return starts, counts, weights


def declaration(name, ctype, array):
  def literal(x):
    if isinstance(x, np.ndarray):
      return '{' + ','.join(literal(v) for v in x) + '}'
    return float(x).hex() + 'f' if isinstance(x, np.floating) else str(int(x))
  dims = ''.join(f'[{n}]' for n in array.shape)
  return f'static const {ctype} {name}{dims} = {literal(array)};\n'


def tables():
  if torch.__version__.split('+')[0] != '2.8.0':
    raise RuntimeError('Table generation requires Torch 2.8.0')
  x = axis(768, 576, 'x', X_SHA256)
  y = axis(432, 320, 'y', Y_SHA256)
  result = ''.join(declaration(label+suffix, ctype, a) for label, values in [('x', x), ('y', y)]
                   for suffix, ctype, a in zip(('i', 'n', 'w'), ('int16_t', 'uint8_t', 'float'), values, strict=True))
  # Twelve interior pixels form three filter phases across four SIMD lanes. Store each actual coefficient.
  phases = np.zeros((48,16,4), dtype=np.float32)
  for block in range(1, 47):
    for lane in range(4):
      for phase, (offset, taps, begin) in enumerate([(-2,5,0), (-1,6,5), (1,5,11)]):
        col = 12*block + 3*lane + phase
        if x[0][col] != 16*block + 4*lane + offset or x[1][col] != taps:
          raise ValueError('Unexpected interior filter layout')
        phases[block, begin:begin+taps, lane] = x[2][col, :taps]
  return result + declaration('phase', 'float', phases)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--output-dir', type=Path, required=True, help='selected package directory in the staging tree')
  parser.add_argument('--cc', default='gcc' if platform.machine() == 'aarch64' else 'aarch64-linux-gnu-gcc')
  args = parser.parse_args()
  if subprocess.check_output([args.cc, '-dumpmachine'], text=True).strip() != 'aarch64-linux-gnu':
    raise RuntimeError('Expected an AArch64 Linux GNU compiler')
  args.output_dir.mkdir(parents=True, exist_ok=True)
  destination = args.output_dir / OBJECT_NAME
  with tempfile.TemporaryDirectory(dir=args.output_dir) as tmp:
    work = Path(tmp).resolve()
    shutil.copyfile(SOURCE/'fresh.c', work/'fresh.c')
    (work/'tables.h').write_text(tables())
    subprocess.run([args.cc, '-O3', '-std=c11', '-shared', '-fPIC', '-Wall', '-Wextra', '-Werror', '-ffp-contract=off',
                    '-fno-fast-math', '-pthread', '-Wl,-z,relro,-z,now', '-march=armv8-a+simd', '-mtune=cortex-a55',
                    'fresh.c', '-lm', '-o', OBJECT_NAME], cwd=work, check=True)
    binary = work/OBJECT_NAME
    if hashlib.sha256(binary.read_bytes()).hexdigest() != OBJECT_SHA256:
      raise RuntimeError('Compiler output differs from the qualified object; check the documented toolchain')
    os.replace(binary, destination)
  print(f'{OBJECT_SHA256}  {destination}')


if __name__ == '__main__':
  main()
