"""C3X upstream compiled-model validation parity without changing C4 chunk cache."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from openpilot.common.file_chunker import get_chunk_name, get_manifest_path
from openpilot.sunnypilot.models import helpers


def sha256(raw: bytes) -> str:
  return hashlib.sha256(raw).hexdigest()


class TestUpstreamTiziModelValidation(unittest.TestCase):
  def setUp(self):
    self.tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self.tmp.cleanup)
    self.dir = Path(self.tmp.name)
    self.full = b"SPTGPLN1" + bytes(range(256)) * 8
    self.parts = [self.full[:len(self.full)//2], self.full[len(self.full)//2:]]
    self.name = "compiled_tinygrad.pkl"
    self.path = self.dir / self.name
    self.chunk_paths = [Path(get_chunk_name(str(self.path), i, 2)) for i in range(2)]
    for path, data in zip(self.chunk_paths, self.parts, strict=True):
      path.write_bytes(data)
    Path(get_manifest_path(str(self.path))).write_text("2")
    self.artifact = SimpleNamespace(
      fileName=self.name,
      downloadUri=SimpleNamespace(sha256=sha256(self.full)),
      chunks=[SimpleNamespace(sha256=sha256(x)) for x in self.parts],
    )
    self.bundle = SimpleNamespace(models=[SimpleNamespace(artifact=self.artifact)])

  def check(self, device: str) -> bool:
    with patch.object(helpers.HARDWARE, "get_device_type", return_value=device), \
         patch.object(helpers.Paths, "model_root", return_value=str(self.dir)):
      return helpers._bundle_is_valid_locally(self.bundle)

  def test_c3x_rejects_chunk_only_model_even_with_matching_hash(self):
    self.assertFalse(self.check("tizi"))
    self.assertFalse(self.path.exists())

  def test_c3x_accepts_complete_verified_pkl(self):
    self.path.write_bytes(self.full)
    self.assertTrue(self.check("tizi"))
    self.path.write_bytes(self.full + b"corrupt")
    self.assertFalse(self.check("tizi"))

  def test_c3x_needs_real_full_pkl_even_with_chunk_metadata(self):
    with patch.object(helpers.HARDWARE, "get_device_type", return_value="tizi"):
      self.assertEqual(helpers._bundle_artifacts(self.bundle), [(self.name, sha256(self.full))])
      self.assertIsNone(helpers._compute_hash(str(self.path)))

  def test_c4_preserves_previous_chunk_cache_behavior(self):
    self.assertTrue(self.check("mici"))
    with patch.object(helpers.HARDWARE, "get_device_type", return_value="mici"):
      artifacts = helpers._bundle_artifacts(self.bundle)
      self.assertEqual(artifacts, [(f"{self.name}.chunk01of02", sha256(self.parts[0])),
                                   (f"{self.name}.chunk02of02", sha256(self.parts[1]))])
      self.assertEqual(helpers._compute_hash(str(self.path)), sha256(self.full))

  def test_c4_detects_corrupt_chunk_as_before(self):
    self.chunk_paths[1].write_bytes(b"corrupt")
    self.assertFalse(self.check("mici"))

  def test_c3x_detects_corrupt_full_file_independent_of_chunks(self):
    self.path.write_bytes(self.full + b"corrupt")
    self.assertFalse(self.check("tizi"))
    self.assertTrue(self.check("mici"))


if __name__ == "__main__":
  unittest.main(verbosity=2)
