"""Pack one calibrated front image into a new checkpoint patch tensor."""
import ctypes
import hashlib
import platform
from functools import lru_cache
from pathlib import Path

import torch

from .native_patches import OBJECT_NAME, OBJECT_SHA256


@lru_cache(maxsize=1)
def library():
  if platform.machine() != 'aarch64' or torch.__version__ != '2.8.0+cpu':
    raise RuntimeError('Native front patches require Linux AArch64 and Torch 2.8.0+cpu')
  path = Path(__file__).with_name(OBJECT_NAME)
  if not path.is_file():
    raise FileNotFoundError(f'Missing {path}. Build the selected native patch library before enabling native_fresh_patches.')
  with path.open('rb') as f:
    if hashlib.file_digest(f, 'sha256').hexdigest() != OBJECT_SHA256:
      raise ValueError('Native front patch library differs from the verified build')
    # Load the same file that was verified, even if the package path is replaced concurrently.
    lib = ctypes.CDLL(f'/proc/self/fd/{f.fileno()}')
  lib.fresh_patch.argtypes = (ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int)
  lib.fresh_patch.restype = ctypes.c_int
  return lib


def pack_fresh(source, workers=2):
  if type(source) is bytes:
    if len(source) != 3*432*768:
      raise ValueError('Wrong immutable camera byte count')
    # The explicit length includes embedded zeros. Keep the owner alive until the native workers join.
    address, length = ctypes.cast(ctypes.c_char_p(source), ctypes.c_void_p), len(source)
  else:
    if source.device.type != 'cpu' or source.dtype != torch.uint8 or tuple(source.shape) != (3,432,768) or not source.is_contiguous():
      raise ValueError('Expected dense CHW uint8 768x432')
    address, length = source.data_ptr(), source.numel()
  out = torch.empty((720,768), dtype=torch.uint8, device='cpu')
  rc = library().fresh_patch(address, length, out.data_ptr(), out.numel(), workers)
  if rc:
    raise RuntimeError(f'Native front patch conversion failed: {rc}')
  return out
