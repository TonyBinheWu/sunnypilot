"""Offline-only reconstruction test. No vehicle or GPU access required."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from openpilot.common.file_chunker import get_chunk_name, get_manifest_path
from openpilot.sunnypilot.models.qcom_repair import repair_qcom_bundle


def digest(blob):
  return hashlib.sha256(blob).hexdigest()


def artifact(name, data, root, *, tamper=False):
  pieces = [data[:len(data)//2], data[len(data)//2:]]
  chunks = [SimpleNamespace(sha256=digest(piece)) for piece in pieces]
  for i, piece in enumerate(pieces):
    Path(get_chunk_name(str(root / name), i, len(pieces))).write_bytes(piece + (b"!" if tamper and i == 1 else b""))
  Path(get_manifest_path(str(root / name))).write_text(str(len(pieces)))
  return SimpleNamespace(fileName=name, chunks=chunks, downloadUri=SimpleNamespace(sha256=digest(data)))


class TestC3XQcomRepair(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.root = Path(self.tmp.name)
    self.raw = b"SPTGPLN1" + bytes(range(256)) * 3000

  def bundle(self, meta):
    return SimpleNamespace(models=[SimpleNamespace(artifact=meta)])

  def test_split_model_is_rebuilt_atomically_with_correct_sha(self):
    meta = artifact("driving.pkl", self.raw, self.root)
    result = repair_qcom_bundle(str(self.root), self.bundle(meta))
    self.assertEqual(result, ["driving.pkl"])
    self.assertEqual((self.root / "driving.pkl").read_bytes(), self.raw)
    self.assertEqual(repair_qcom_bundle(str(self.root), self.bundle(meta)), [])
    self.assertEqual(list(self.root.glob(".qcom-repair-*")), [])

  def test_manifest_only_model_index_is_supported(self):
    # Upstream driving_models_v25.json publishes a full SHA, but omits
    # artifact.chunks even when model.type is "chunked".
    meta = artifact("driving.pkl", self.raw, self.root)
    meta.chunks = []
    self.assertEqual(repair_qcom_bundle(str(self.root), self.bundle(meta)), ["driving.pkl"])
    self.assertEqual((self.root / "driving.pkl").read_bytes(), self.raw)

  def test_manifest_only_bad_full_sha_is_rejected(self):
    meta = artifact("driving.pkl", self.raw, self.root, tamper=True)
    meta.chunks = []
    with self.assertRaisesRegex(ValueError, "model checksum mismatch"):
      repair_qcom_bundle(str(self.root), self.bundle(meta))
    self.assertFalse((self.root / "driving.pkl").exists())

  def test_corrupt_chunk_does_not_replace_model(self):
    meta = artifact("driving.pkl", self.raw, self.root, tamper=True)
    with self.assertRaisesRegex(ValueError, "checksum mismatch"):
      repair_qcom_bundle(str(self.root), self.bundle(meta))
    self.assertFalse((self.root / "driving.pkl").exists())
    self.assertEqual(list(self.root.glob(".qcom-repair-*")), [])

  def test_already_verified_full_model_is_unchanged(self):
    meta = artifact("driving.pkl", self.raw, self.root, tamper=True)
    full = self.root / "driving.pkl"
    full.write_bytes(self.raw)
    self.assertEqual(repair_qcom_bundle(str(self.root), self.bundle(meta)), [])
    self.assertEqual(full.read_bytes(), self.raw)

  def test_wrong_manifest_never_repairs(self):
    meta = artifact("driving.pkl", self.raw, self.root)
    Path(get_manifest_path(str(self.root / "driving.pkl"))).write_text("3")
    self.assertEqual(repair_qcom_bundle(str(self.root), self.bundle(meta)), [])
    self.assertFalse((self.root / "driving.pkl").exists())

  def test_insufficient_space_fails_closed(self):
    meta = artifact("driving.pkl", self.raw, self.root)
    with patch("openpilot.sunnypilot.models.qcom_repair.shutil.disk_usage",
               return_value=SimpleNamespace(free=1024)):
      with self.assertRaisesRegex(OSError, "insufficient"):
        repair_qcom_bundle(str(self.root), self.bundle(meta))
    self.assertFalse((self.root / "driving.pkl").exists())

  def test_traversal_is_rejected(self):
    meta = artifact("driving.pkl", self.raw, self.root)
    meta.fileName = "../../outside.pkl"
    with self.assertRaisesRegex(ValueError, "escapes"):
      repair_qcom_bundle(str(self.root), self.bundle(meta))


if __name__ == "__main__":
  unittest.main(verbosity=2)
