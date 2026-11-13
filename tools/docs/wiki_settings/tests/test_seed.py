import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
  SPEC = importlib.util.spec_from_file_location("wiki_settings_seed", ROOT / "seed.py")
  SEED = importlib.util.module_from_spec(SPEC)
  SPEC.loader.exec_module(SEED)
finally:
  sys.path.pop(0)

BUNDLED = ROOT.parents[2] / "openpilot/selfdrive/carrot/web/docs/settings"


class SeedTest(unittest.TestCase):
  def test_imports_traditional_guide_and_is_idempotent_preserving_wiki_edits(self):
    with tempfile.TemporaryDirectory() as directory:
      wiki = Path(directory)
      home = wiki / "Home.md"
      home.write_text("# Keep this home\n", encoding="utf-8")
      self.assertEqual(SEED.seed_missing_guides(BUNDLED, wiki), 852)
      page = wiki / "ZH-TW-語音播報音量.md"
      self.assertIn("### 使用方式", page.read_text(encoding="utf-8"))
      renamed = wiki / "ZH-TW-Custom-title.md"
      page.rename(renamed)
      edited = renamed.read_text(encoding="utf-8").replace("### 使用方式", "### 使用方式\n\nExisting Wiki edit.")
      renamed.write_text(edited, encoding="utf-8")
      self.assertEqual(SEED.seed_missing_guides(BUNDLED, wiki), 0)
      self.assertEqual(renamed.read_text(encoding="utf-8"), edited)
      self.assertFalse(page.exists())
      self.assertEqual(home.read_text(encoding="utf-8"), "# Keep this home\n")

  def test_unmanaged_collision_prevents_all_imports(self):
    with tempfile.TemporaryDirectory() as directory:
      wiki = Path(directory)
      page = wiki / "ZH-TW-語音播報音量.md"
      page.write_text("# Keep this page\n", encoding="utf-8")
      with self.assertRaises(SEED.generate.GenerationError):
        SEED.seed_missing_guides(BUNDLED, wiki)
      self.assertEqual(list(wiki.iterdir()), [page])


if __name__ == "__main__":
  unittest.main()
