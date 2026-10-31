"""Offroad-only repair of split QCOM tinygrad artifacts on comma 3X.

The model index can describe verified *.chunk files while modeld_v2 expects
an actual mmap-able combined *.pkl. Never run this from a driving process.
"""
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

from openpilot.common.file_chunker import get_chunk_name, get_manifest_path

COPY_SIZE = 4 * 1024 * 1024


def invalid_qcom_models(model_root: str, bundle) -> list[str]:
  """Return missing or corrupt compiled model paths for offroad recovery."""
  if bundle is None:
    return []
  root = Path(model_root).resolve()
  invalid = []
  for model in bundle.models:
    artifact = model.artifact
    name = artifact.fileName
    if not name or not name.endswith(".pkl"):
      continue
    target = root / name
    if not target.resolve().is_relative_to(root) or target.is_symlink():
      raise ValueError("model artifact path escapes model storage")
    if not target.is_file():
      invalid.append(name)
      continue
    expected = getattr(artifact.downloadUri, "sha256", None)
    if expected:
      digest = hashlib.sha256()
      with target.open("rb") as source:
        for block in iter(lambda: source.read(COPY_SIZE), b""):
          digest.update(block)
      if digest.hexdigest().lower() != str(expected).lower():
        invalid.append(name)
  return invalid


def repair_qcom_bundle(model_root: str, bundle) -> list[str]:
  """Reconstruct missing full model files, after verifying all source chunks.

  Files are made visible atomically only after integrity checks pass. Never delete
  the original chunks or change the selected model, runner, or control parameters.
  """
  if bundle is None:
    return []
  root = Path(model_root).resolve()
  repaired: list[str] = []
  for model in bundle.models:
    artifact = model.artifact
    name = artifact.fileName
    if not name or not name.endswith(".pkl"):
      continue
    target = root / name
    if not target.resolve().is_relative_to(root) or target.is_symlink():
      raise ValueError("model artifact path escapes model storage")
    chunks = list(getattr(artifact, "chunks", ()) or ())
    manifest = Path(get_manifest_path(str(target)))
    if not manifest.is_file() or manifest.is_symlink():
      continue
    try:
      count = int(manifest.read_text().strip())
    except ValueError:
      continue
    if not 1 <= count <= 256 or (chunks and len(chunks) != count):
      continue
    files = [Path(get_chunk_name(str(target), i, count)) for i in range(count)]
    if any(not p.is_file() or p.is_symlink() for p in files):
      continue
    expected_hash = getattr(artifact.downloadUri, "sha256", None)
    # Official QCOM index often has an artifact SHA without per-chunk SHAs.
    # In that case the final SHA256 is still sufficient to verify the entire file.
    if not expected_hash and (not chunks or not all(getattr(chunk, "sha256", None) for chunk in chunks)):
      continue
    # If the full file is already verified, leave the normal runtime unchanged.
    if target.is_file() and expected_hash:
      existing = hashlib.sha256()
      with target.open("rb") as source:
        for block in iter(lambda: source.read(COPY_SIZE), b""):
          existing.update(block)
      if existing.hexdigest().lower() == str(expected_hash).lower():
        continue
    total = sum(p.stat().st_size for p in files)
    if total < 8 or shutil.disk_usage(root).free <= total + 64 * 1024 * 1024:
      raise OSError("insufficient model data or disk space to reconstruct QCOM model")
    fd, tmp = tempfile.mkstemp(prefix=".qcom-repair-", suffix=".pkl", dir=root)
    try:
      whole_digest = hashlib.sha256()
      with os.fdopen(fd, "wb") as output:
        for i, source_path in enumerate(files):
          chunk_digest = hashlib.sha256()
          with source_path.open("rb") as source:
            for block in iter(lambda: source.read(COPY_SIZE), b""):
              chunk_digest.update(block)
              whole_digest.update(block)
              output.write(block)
          if chunks and chunk_digest.hexdigest().lower() != str(chunks[i].sha256).lower():
            raise ValueError(f"QCOM model chunk checksum mismatch: {source_path.name}")
        output.flush()
        os.fsync(output.fileno())
      if expected_hash and whole_digest.hexdigest().lower() != str(expected_hash).lower():
        raise ValueError(f"QCOM model checksum mismatch: {name}")
      with open(tmp, "rb") as check:
        if check.read(8) != b"SPTGPLN1":
          raise ValueError(f"QCOM model is not a supported compiled tinygrad bundle: {name}")
      os.replace(tmp, target)
      repaired.append(name)
    finally:
      Path(tmp).unlink(missing_ok=True)
  return repaired
