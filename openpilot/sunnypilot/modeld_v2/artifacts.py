import json
import os
from pathlib import Path
from typing import BinaryIO

MAGIC = b"SPTGPLN1"
MODELS_DIR = Path(__file__).resolve().parent / "models"


def find_driving_pkl(bundle) -> str | None:
  override = os.environ.get("COMBINED_MODEL_PKL")
  if override and os.path.isfile(override):
    return override
  if bundle is None or not bundle.models:
    return None
  from openpilot.common.hardware.hw import Paths
  path = os.path.join(Paths.model_root(), bundle.models[0].artifact.fileName)
  return path if os.path.isfile(path) else None


def _header_size(f: BinaryIO) -> int:
  if f.read(len(MAGIC)) != MAGIC:
    return 0
  size = int.from_bytes(f.read(8), "little")
  return size if 0 < size < os.fstat(f.fileno()).st_size - f.tell() else 0


def _has_plain_warp(w: int, h: int) -> bool:
  try:
    with (MODELS_DIR / f"big_driving_warp_{w}x{h}_tinygrad.pkl").open("rb") as f:
      return _header_size(f) > 0
  except OSError:
    return False


def chestnut_bundle_available(bundle) -> bool:
  from openpilot.selfdrive.modeld.helpers import CHESTNUT_CAMERA_SIZES
  path = find_driving_pkl(bundle)
  if path is None:
    return False
  try:
    with open(path, "rb") as f:
      header_size = _header_size(f)
      if not header_size:
        return False
      missing = [list(size) for size in CHESTNUT_CAMERA_SIZES if not _has_plain_warp(*size)]
      if not missing:
        return True
      # Legacy bundles can carry their own per-camera warp. Native 'run' needs the external warp for fusion.
      keys = [part["key"] for part in json.loads(f.read(header_size))["parts"]]
      return "run" not in keys and all(size in keys for size in missing)
  except (OSError, ValueError, KeyError, TypeError):
    return False
