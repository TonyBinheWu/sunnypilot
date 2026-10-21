import json
import re
import string
from pathlib import Path


from openpilot.common.parameterized import parameterized
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.translations.potools import parse_po
from openpilot.system.ui.lib.multilang import LANGUAGES_FILE, TRANSLATIONS_DIR

PERCENT_PLACEHOLDER_RE = re.compile(r"%(?:n|\d+)")
BAD_ENTITY_RE = re.compile(r'@(\w+);')
LINE_NUMBER_REF_RE = re.compile(r'^#:\s+.+:\d+(?:\s|$)')
FORMATTER = string.Formatter()
PO_DIR = Path(str(TRANSLATIONS_DIR))

with LANGUAGES_FILE.open(encoding='utf-8') as f:
  TRANSLATION_LANGUAGES = json.load(f)


def extract_placeholders(text: str) -> list[str]:
  placeholders = PERCENT_PLACEHOLDER_RE.findall(text)

  try:
    parsed = list(FORMATTER.parse(text))
  except ValueError as e:
    raise AssertionError(f"invalid brace formatting in {text!r}: {e}") from e

  for _, field_name, format_spec, conversion in parsed:
    if field_name is None:
      continue

    token = "{"
    token += field_name
    if conversion:
      token += f"!{conversion}"
    if format_spec:
      token += f":{format_spec}"
    token += "}"
    placeholders.append(token)

  return sorted(placeholders)


def load_po_text(po_path: Path) -> str:
  return po_path.read_text(encoding='utf-8')


class TestTranslations(OpenpilotTestCase):
  def test_traditional_chinese_ccnc_is_selectable(self):
    assert "zh-CHT" in TRANSLATION_LANGUAGES.values()
    assert TRANSLATION_LANGUAGES["中文（繁體）"] == "zh-CHT"
    from openpilot.system.ui.lib.multilang import load_translations
    translations, _ = load_translations(PO_DIR / "app_zh-CHT.po")
    assert translations["Change Language"] == "變更語言"
    assert translations["HKG Low-Speed Steering Torque (Experimental)"] == "HKG 低速轉向扭力（實驗功能）"
    # The comma 4 Device > Change Language picker must expose the same
    # localized option and callback as the tested hkg-enhanced UI.
    device_source = (Path(__file__).parents[1] / "layouts/settings/device.py").read_text(encoding="utf-8")
    assert 'callback=self._show_language_dialog' in device_source
    assert 'MultiOptionDialog(tr("Select a language"), multilang.languages' in device_source
    assert "multilang.change_language(selected_language)" in device_source



  def test_mici_traditional_chinese_menu_and_safety_warnings(self):
    """comma 4 Mici has its own string consumers, separate from the classic UI."""
    from openpilot.system.ui.lib.multilang import load_translations

    translations, _ = load_translations(PO_DIR / "app_zh-CHT.po")
    expected = {
      "toggles": "功能開關",
      "network": "網路",
      "device": "裝置",
      "software": "軟體",
      "developer": "開發者",
      "firehose": "資料分享",
      "models": "模型",
      "slide to exit always offroad": "滑動以離開持續停駛模式",
      "slide to force offroad": "滑動以強制進入停駛模式",
      "enabling\\nexperimental mode": "啟用\\n實驗模式",
      "WARNING: alpha longitudinal control may disable Automatic Emergency Braking (AEB)":
        "警告：Alpha 縱向控制可能使原廠自動緊急煞車（AEB）失效。",
    }
    for source, translated in expected.items():
      assert translations.get(source) == translated, f"Missing comma 4 Chinese translation: {source!r}"

  def test_mici_localized_labels_refresh_after_language_change(self):
    button_py = (Path(__file__).parents[1] / "mici/widgets/button.py").read_text(encoding="utf-8")
    assert "self._label = UnifiedLabel(tr(text)" in button_py
    assert "self._sub_label = UnifiedLabel(tr(value)" in button_py
    assert "self._label.set_text(tr(self.text))" in button_py
    assert "self._sub_label.set_text(tr(self.value))" in button_py
    assert "self._locale_when_rendered != multilang.language" in button_py
    assert "self.value = value" in button_py  # Parameter options remain raw, not translated.

  def test_mici_translation_markers_are_extracted(self):
    from openpilot.selfdrive.ui.translations.potools import extract_strings

    base = Path(__file__).resolve().parents[4]
    relative = "openpilot/selfdrive/ui/mici/layouts/settings/translation_catalog.py"
    extracted = {entry.msgid for entry in extract_strings([relative], str(base))}
    for key in ("toggles", "network", "device", "developer", "slide to exit always offroad",
                "WARNING: alpha longitudinal control may disable Automatic Emergency Braking (AEB)"):
      assert key in extracted, f"Mici translation marker missing: {key}"


  @parameterized.expand(sorted(TRANSLATION_LANGUAGES.values()))
  def test_translation_file_exists(self, language_code: str):
    po_path = PO_DIR / f"app_{language_code}.po"
    assert po_path.exists(), f"missing translation file: {po_path}"

  @parameterized.expand(sorted(PO_DIR.glob("app_*.po")), ids=lambda p: p.name)
  def test_translation_placeholders_are_preserved(self, po_path: Path):
    _, entries = parse_po(po_path)
    language = po_path.stem.removeprefix("app_")

    for entry in entries:
      source_placeholders = extract_placeholders(entry.msgid)

      if entry.is_plural:
        plural_placeholders = extract_placeholders(entry.msgid_plural)
        message = (
          f"{language}: source plural placeholders do not match singular for "
          + f"{entry.msgid!r}: {source_placeholders} vs {plural_placeholders}"
        )
        assert plural_placeholders == source_placeholders, message

        for idx, msgstr in sorted(entry.msgstr_plural.items()):
          if not msgstr:
            continue

          translated_placeholders = extract_placeholders(msgstr)
          message = (
            f"{language}: plural form {idx} changes placeholders for {entry.msgid!r}: "
            + f"expected {source_placeholders}, got {translated_placeholders}"
          )
          assert translated_placeholders == source_placeholders, message
      else:
        if not entry.msgstr:
          continue

        translated_placeholders = extract_placeholders(entry.msgstr)
        message = (
          f"{language}: translation changes placeholders for {entry.msgid!r}: "
          + f"expected {source_placeholders}, got {translated_placeholders}"
        )
        assert translated_placeholders == source_placeholders, message

  @parameterized.expand(sorted(PO_DIR.glob("app_*.po")), ids=lambda p: p.name)
  def test_translation_refs_do_not_include_line_numbers(self, po_path: Path):
    for line in load_po_text(po_path).splitlines():
      assert not LINE_NUMBER_REF_RE.match(line), (
        f"{po_path.name}: line-number source reference found: {line}"
      )

  @parameterized.expand(sorted(PO_DIR.glob("app_*.po")), ids=lambda p: p.name)
  def test_translation_entities_are_valid(self, po_path: Path):
    matches = BAD_ENTITY_RE.findall(load_po_text(po_path))
    assert not matches, (
      f"{po_path.name}: found '@...;' entity typo(s): {', '.join(sorted(set(matches)))}"
    )
