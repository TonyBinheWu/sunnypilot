"""Keep complete Traditional translations tied to the exact upstream prose."""
from copy import deepcopy
import json
import unittest

from tools.docs.wiki_settings.build_traditional_bundle import TRANSLATIONS, translated_manual
from tools.docs.wiki_settings.generate import REPO_ROOT, scan_existing_settings


class TraditionalManualTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))["settings"]
    cls.existing, _ = scan_existing_settings(REPO_ROOT / "openpilot/selfdrive/carrot/web/docs/settings")

  def test_every_detailed_english_guide_has_traditional_sections(self):
    for (locale, param), item in self.existing.items():
      if locale != "en":
        continue
      traditional = self.existing["zh-tw", param].manual_block
      if "<!-- CARROT:SECTION:BEGIN" in item.manual_block:
        self.assertIn("<!-- CARROT:SECTION:BEGIN BEHAVIOR -->", traditional, param)

  def test_all_overlay_translations_match_source_and_bundled_manual(self):
    self.assertEqual(len(self.translations), 140)
    for param, entry in self.translations.items():
      english = self.existing["en", param].manual_block
      manual = self.existing["zh-tw", param].manual_block
      self.assertEqual(entry["manual"], manual, param)
      self.assertEqual(translated_manual(param, english, manual, self.translations), manual)
      self.assertNotIn("### Behavior", manual, param)
      self.assertNotIn("### Usage", manual, param)
      self.assertNotIn("### Reference", manual, param)

  def test_changed_source_requires_translation_review(self):
    english = self.existing["en", "PathOffset"].manual_block
    manual = self.existing["zh-tw", "PathOffset"].manual_block
    with self.assertRaisesRegex(ValueError, "English guide changed"):
      translated_manual("PathOffset", english + "\nChanged behavior", manual, self.translations)

  def test_changed_values_or_markers_are_rejected(self):
    param = "AutoCruiseControl"
    english = self.existing["en", param].manual_block
    manual = self.existing["zh-tw", param].manual_block
    for old, new in (("`0`", "`9`"), ("SECTION:BEGIN BEHAVIOR", "SECTION:BEGIN USAGE")):
      changed = deepcopy(self.translations)
      changed[param]["manual"] = manual.replace(old, new, 1)
      with self.assertRaises(ValueError):
        translated_manual(param, english, manual, changed)

  def test_untranslated_entries_preserve_original_manual(self):
    self.assertEqual(translated_manual("OtherSetting", "English", "Original", {}), "Original")
