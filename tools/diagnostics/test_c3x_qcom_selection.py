"""C3X vs C4 model source validation regression (run after compiled imports)."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from openpilot.cereal import custom
from openpilot.common.file_chunker import get_chunk_name, get_manifest_path
from openpilot.sunnypilot.models import helpers


def digest(b):
  return hashlib.sha256(b).hexdigest()


class TestC3XQcomRuntimeValidation(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.root = Path(self.tmp.name)
    data = b"SPTGPLN1" + bytes(range(256)) * 10
    self.full = data
    parts = [data[:len(data)//2], data[len(data)//2:]]
    self.chunk_paths = [self.root / get_chunk_name("driving.pkl", i, 2) for i in range(2)]
    for p, content in zip(self.chunk_paths, parts, strict=True):
      p.write_bytes(content)
    Path(get_manifest_path(str(self.root / "driving.pkl"))).write_text("2")
    art = SimpleNamespace(fileName="driving.pkl", chunks=[SimpleNamespace(sha256=digest(x)) for x in parts],
                          downloadUri=SimpleNamespace(sha256=digest(data)))
    self.meta = art
    self.bundle = SimpleNamespace(runner=custom.ModelManagerSP.Runner.tinygrad,
                                  models=[SimpleNamespace(artifact=art)])
    self.path = self.root / "driving.pkl"

  def valid(self, hardware, source):
    with patch.object(helpers.Paths, "model_root", return_value=str(self.root)), \
         patch.object(helpers.HARDWARE, "get_device_type", return_value=hardware):
      return helpers._bundle_is_valid_locally(self.bundle, source)

  def test_tizi_rejects_chunks_without_runtime_pkl(self):
    self.assertFalse(self.valid("tizi", "qcom"))

  def test_mici_keeps_previous_validation_behavior(self):
    self.assertTrue(self.valid("mici", "qcom"))

  def test_official_manifest_only_index_differentiates_c3x_c4(self):
    self.meta.chunks = []
    self.assertTrue(self.valid("mici", "qcom"))
    self.assertFalse(self.valid("tizi", "qcom"))
    self.path.write_bytes(self.full)
    self.assertTrue(self.valid("tizi", "qcom"))

  def test_tizi_accepts_verified_runtime_pkl_without_chunks(self):
    self.path.write_bytes(self.full)
    for path in self.chunk_paths:
      path.unlink()
    self.assertTrue(self.valid("tizi", "qcom"))

  def test_tizi_rejects_corrupt_runtime_pkl(self):
    self.path.write_bytes(self.full + b"tamper")
    self.assertFalse(self.valid("tizi", "qcom"))

  def test_chestnut_source_does_not_change(self):
    self.assertTrue(self.valid("tizi", "chestnut"))


if __name__ == "__main__":
  unittest.main(verbosity=2)
