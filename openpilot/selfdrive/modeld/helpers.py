import os
import sys
import time
from pathlib import Path

from openpilot.common.hardware import AGNOS
from openpilot.common.hardware.usb import CHESTNUT_USB_PRODUCT, USB_DEVICES_PATH, is_chestnut_usb_id

MODELS_DIR = Path(__file__).resolve().parent / 'models'
CHESTNUT_CAMERA_SIZES = ((1344, 760), (1928, 1208))


def modeld_pkl_path(chestnut: bool):
  prefix = 'big_' if chestnut else ''
  return MODELS_DIR / f'{prefix}driving_tinygrad.pkl'

def load_oob(path, chestnut=False):
  from tinygrad import Context
  device = 'USB+AMD:LLVM' if chestnut else 'QCOM' if AGNOS else 'METAL' if sys.platform == 'darwin' else 'CPU:LLVM'
  with Context(DEV=device):
    from tinygrad_repo.examples.openpilot.helpers import load_pickle
    return load_pickle(path, out_of_band=True)

def chestnut_present() -> bool:
  for d in USB_DEVICES_PATH.glob("*"):
    try:
      usb_id = (int((d / "idVendor").read_text(), 16), int((d / "idProduct").read_text(), 16))
      product = (d / "product").read_text().strip()
      if is_chestnut_usb_id(*usb_id) and product == CHESTNUT_USB_PRODUCT:
        return True
    except Exception:
      pass
  return False

def wait_for_chestnut(timeout: float = 10.) -> None:
  # the cable is detected before chestnut enumerates
  st = time.monotonic()
  while not chestnut_present():
    if time.monotonic() - st > timeout:
      raise TimeoutError("chestnut did not enumerate")
    time.sleep(0.1)

def _has_pickle(path: Path, *, out_of_band: bool = False) -> bool:
  try:
    with path.open('rb') as f:
      if out_of_band:
        # The stock model starts with an opcode length, followed by the pickle and weights.
        length = int.from_bytes(f.read(8), 'little')
        if not 0 < length < os.fstat(f.fileno()).st_size - 8:
          return False
      if f.read(1) != b'\x80':
        return False
      if out_of_band:
        f.seek(8 + length - 1)
      else:
        f.seek(-1, os.SEEK_END)
      return f.read(1) == b'.'  # STOP opcode
  except OSError:
    return False


def chestnut_compiled() -> bool:
  return _has_pickle(modeld_pkl_path(chestnut=True), out_of_band=True) and all(
    _has_pickle(MODELS_DIR / f'big_driving_warp_{w}x{h}_tinygrad.pkl') for w, h in CHESTNUT_CAMERA_SIZES)
