from pathlib import Path
import tempfile
import unittest

from openpilot.common.markdown import parse_markdown
from openpilot.common.release_notes import read_release_notes, release_notes_lines
from tools.release.check_release_notes import check_release_notes
from openpilot.selfdrive.ui.translations.potools import extract_strings, parse_po


class TestReleaseNotes(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.addCleanup(self.directory.cleanup)
    self.root = Path(self.directory.name)

  def write(self, text):
    (self.root / "CHANGELOG.md").write_text(text, encoding="utf-8", newline="\n")

  def test_new_and_installed_trees_do_not_share_notes(self):
    self.write("已安裝版本\n========\n* 舊版功能\n")
    with tempfile.TemporaryDirectory() as staged:
      Path(staged, "CHANGELOG.md").write_text("待更新版本\n========\n* 新版修正\n", encoding="utf-8")
      self.assertTrue("新版修正" in read_release_notes(staged))
      self.assertNotIn("舊版功能", read_release_notes(staged))
      self.assertTrue("舊版功能" in read_release_notes(str(self.root)))

  def test_complete_latest_entry_with_blank_lines_and_crlf(self):
    self.write("新版\n========\n\n* 第一項\n\n* 最後一項\n\n舊版\n========\n* 不應出現\n")
    path = self.root / "CHANGELOG.md"
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    notes = read_release_notes(str(self.root))
    self.assertTrue("最後一項" in notes)
    self.assertNotIn("不應出現", notes)
    self.assertNotIn("\r", notes)

  def test_legacy_notes_without_underlined_heading(self):
    self.write("舊格式\n* 保留內容\n\n歷史版本\n")
    self.assertEqual(read_release_notes(str(self.root)), "舊格式\n* 保留內容")

  def test_ui_lines_keep_chinese_items_and_decode_entities(self):
    html = parse_markdown("更新項目\n========\n* C3X：修正 & 改善\n* C4：完整更新說明\n")
    self.assertEqual(release_notes_lines(html), ["更新項目", "• C3X：修正 & 改善", "• C4：完整更新說明"])
    self.assertEqual(release_notes_lines(""), [])

  def test_both_branch_releases_and_old_updater(self):
    header = self.root / "openpilot/sunnypilot/common/version.h"
    header.parent.mkdir(parents=True)
    header.write_text('#define SUNNYPILOT_VERSION "2026.003.001"\n', encoding="utf-8")
    for branch in ("hkg-enhanced", "ccnc-port"):
      with self.subTest(branch=branch):
        self.write(f"sunnypilot {branch} Version 2026.003.001 (2026-10-31)\n========\n"
                   + "* C3X：更新說明\n* C4：更新說明\n\n舊版\n========\n* 舊項目\n")
        check_release_notes(self.root)
        check_release_notes(self.root, expected_branch=branch)
        other_branch = "ccnc-port" if branch == "hkg-enhanced" else "hkg-enhanced"
        with self.assertRaises(ValueError):
          check_release_notes(self.root, expected_branch=other_branch)
        legacy = (self.root / "CHANGELOG.md").read_bytes().split(b"\n\n", 1)[0]
        self.assertEqual(legacy.decode("utf-8"), read_release_notes(str(self.root)))

  def test_reject_stale_version_and_notes_truncated_by_old_updater(self):
    header = self.root / "openpilot/sunnypilot/common/version.h"
    header.parent.mkdir(parents=True)
    header.write_text('#define SUNNYPILOT_VERSION "2026.003.001"\n', encoding="utf-8")
    for entry in (
      "sunnypilot hkg-enhanced Version 2026.003.000 (2026-10-31)\n========\n* C3X、C4：更新\n",
      "sunnypilot hkg-enhanced Version 2026.003.001 (2026-10-31)\n========\n\n* C3X、C4：更新\n",
      "sunnypilot hkg-enhanced Version 2026.003.001 (2026-10-31)\n========\n* C3X and C4: update\n",
    ):
      self.write(entry)
      with self.assertRaises(ValueError):
        check_release_notes(self.root)

  def test_update_buttons_have_extractable_chinese_translations(self):
    root = Path(__file__).resolve().parents[3]
    entries = extract_strings(["openpilot/selfdrive/ui/mici/layouts/settings/software.py"], str(root))
    sources = {entry.msgid for entry in entries}
    _, translated = parse_po(root / "openpilot/selfdrive/ui/translations/app_zh-CHT.po")
    messages = {entry.msgid: entry.msgstr for entry in translated}
    self.assertTrue("Update notes" in sources)
    self.assertTrue("Installed version notes" in sources)
    self.assertEqual(messages["Update notes"], "更新項目")
    self.assertEqual(messages["Installed version notes"], "目前版本更新說明")


if __name__ == "__main__":
  unittest.main()
