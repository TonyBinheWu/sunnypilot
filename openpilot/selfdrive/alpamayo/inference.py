"""Pinned source revisions of the isolated Alpamayo runtime."""
import hashlib
from pathlib import Path
import subprocess

TINYGRAD_REVISION = '89846dcfb383a98ee01cfec3bba440ae7dcf9b1e'
NVIDIA_REVISION = '02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e'


def sha(path):
  with Path(path).open('rb') as stream:
    return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_runtime():
  import alpamayo2_edge
  import tinygrad
  sources = ((Path(tinygrad.__file__).resolve().parents[1], TINYGRAD_REVISION),
             (Path(alpamayo2_edge.__file__).resolve().parents[2], NVIDIA_REVISION))
  for root, expected in sources:
    revision = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != expected:
      raise RuntimeError(f'Alpamayo requires isolated source revision {expected}')
    if subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', '--untracked-files=no'], text=True).strip():
      raise RuntimeError(f'Modified runtime source: {root.name}')
