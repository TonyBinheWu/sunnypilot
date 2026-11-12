"""Check the real font repertoire, generated bitmap and incremental build graph."""
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from openpilot.selfdrive.ui.translations.potools import parse_po

ROOT = Path(__file__).resolve().parents[4]
FONT_DIR = ROOT / "openpilot/selfdrive/assets/fonts"
TRANSLATIONS = ROOT / "openpilot/selfdrive/ui/translations"


def cjk_characters(text):
  return {c for c in text if '\u3000' <= c <= '\u30ff' or '\u3400' <= c <= '\u9fff'
          or '\uf900' <= c <= '\ufaff' or '\uff00' <= c <= '\uffef'}


def traditional_characters():
  _, entries = parse_po(TRANSLATIONS / "app_zh-CHT.po")
  texts = [value for e in entries for value in [e.msgstr, *e.msgstr_plural.values()]]
  # Emoji have a separate renderer and are not supplied by the CJK text font.
  return cjk_characters(''.join(texts))


def device_characters():
  needed = traditional_characters()
  for path in (ROOT / 'openpilot/sunnypilot/formosalink').glob('*ui.py'):
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
      if isinstance(node, ast.Constant) and isinstance(node.value, str):
        needed.update(cjk_characters(node.value))
  return needed


def generated_codepoints():
  path = FONT_DIR / "process.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  tree.body = [n for n in tree.body if isinstance(n, (ast.Assign, ast.FunctionDef))]
  scope = {"__file__": str(path), "Path": Path}
  exec(compile(tree, str(path), "exec"), scope)
  scope['json'] = json
  return set(scope['_char_sets']()[1])


def test_all_traditional_text_and_punctuation_are_in_generated_subset():
  needed = device_characters() | set("『繁體中文：設定、駕駛與雷達。』")
  assert {ord(c) for c in needed} <= generated_codepoints()


def test_actual_display_font_has_traditional_glyphs():
  ttlib = pytest.importorskip("fontTools.ttLib")
  with ttlib.TTFont(FONT_DIR / 'KaiGenGothicKR-Bold.ttf') as font:
    cmap = font.getBestCmap()
    missing = sorted(c for c in device_characters() if ord(c) not in cmap)
    assert not missing, ''.join(missing)


def test_built_atlas_has_real_traditional_glyph_bitmaps():
  atlas = FONT_DIR / 'KaiGenGothicKR-Bold.fnt'
  if not atlas.exists() and os.getenv('CARROT_REQUIRE_FONT_ATLAS') != '1':
    pytest.skip('requires the generated production font atlas')
  assert atlas.exists(), 'SCons did not build the multilingual atlas'
  fields = {}
  for line in atlas.read_text(encoding='utf-8').splitlines():
    if line.startswith('char id='):
      item = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
      fields[item['id']] = item
  image_module = pytest.importorskip('PIL.Image')
  with image_module.open(atlas.with_suffix('.png')) as image:
    for char in device_characters():
      assert ord(char) in fields, f'{char}: missing atlas entry'
      item = fields[ord(char)]
      assert item['xadvance'] > 0, char
      if char == '\u3000':
        continue  # Ideographic space intentionally has no ink.
      assert item['width'] > 0 and item['height'] > 0, char
      crop = image.crop((item['x'], item['y'], item['x'] + item['width'], item['y'] + item['height']))
      alpha = crop.getchannel('A') if 'A' in crop.getbands() else crop
      assert alpha.getbbox(), f'{char}: empty glyph bitmap'


def test_translation_only_changes_rebuild_font_atlases(tmp_path):
  pytest.importorskip('SCons')
  root = tmp_path / 'font-build'
  fonts = root / 'openpilot/selfdrive/assets/fonts'
  translations = root / 'openpilot/selfdrive/ui/translations'
  fonts.mkdir(parents=True)
  translations.mkdir(parents=True)
  shutil.copy2(ROOT / 'openpilot/selfdrive/ui/SConscript', root / 'openpilot/selfdrive/ui/SConscript')
  (fonts / 'Fixture.ttf').write_text('build-graph fixture only', encoding='utf-8')
  # Drive the production SConscript with a cheap generator. Raster correctness
  # is checked separately against the production-built atlas above.
  (fonts / 'process.py').write_text(
    'from pathlib import Path\nfrom uuid import uuid4\n'
    'for p in Path(__file__).parent.glob("*.ttf"):\n'
    ' for ext in (".fnt", ".png"):\n'
    '  p.with_suffix(ext).write_text(str(uuid4()))\n', encoding='utf-8')
  po = translations / 'app_zh-CHT.po'
  po.write_text('msgstr "設定"\n', encoding='utf-8')
  languages = translations / 'languages.json'
  languages.write_text('{"中文（繁體）":"zh-CHT"}', encoding='utf-8')
  (root / 'SConstruct').write_text(
    'import os\nAddOption("--extras", action="store_true", default=False)\n'
    'env = Environment(ENV=dict(os.environ))\narch = "desktop"\ncommon = []\n'
    'Export("env", "arch", "common")\nSConscript("openpilot/selfdrive/ui/SConscript")\n', encoding='utf-8')
  env = dict(os.environ)
  if sys.platform == 'win32':
    (root / 'python3.cmd').write_text(f'@"{sys.executable}" %*\n', encoding='utf-8')
    env['PATH'] = str(root) + os.pathsep + env['PATH']

  def build():
    result = subprocess.run([sys.executable, '-m', 'SCons', '-Q'], cwd=root, env=env,
                            capture_output=True, text=True, encoding='utf-8', timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    return (fonts / 'Fixture.fnt').read_text()

  first = build()
  assert build() == first
  po.write_text('msgstr "駕駛與雷達設定"\n', encoding='utf-8')
  changed_translation = build()
  assert changed_translation != first, 'translation update reused the stale atlas'
  languages.write_text('{"中文（繁體）":"zh-CHT", "한국어":"ko"}', encoding='utf-8')
  changed_languages = build()
  assert changed_languages != changed_translation
  (translations / 'app_ja.po').write_text('msgstr "設定"\n', encoding='utf-8')
  changed_catalog = build()
  assert changed_catalog != changed_languages, 'a newly installed catalog did not rebuild fonts'
  native_ui = root / 'openpilot/sunnypilot/formosalink/ui.py'
  native_ui.parent.mkdir(parents=True)
  native_ui.write_text('TEXT = "遠端 Carrot 網頁"\n', encoding='utf-8')
  changed_native = build()
  assert changed_native != changed_catalog, 'native UI dictionaries did not rebuild fonts'
  native_ui.write_text('TEXT = "遠端 Carrot 網頁：關"\n', encoding='utf-8')
  assert build() != changed_native, 'native UI text changes reused a stale atlas'


@pytest.mark.parametrize('label', ['沒有警示', '外接 GPU', '遠端 Carrot 網頁', '掃描 QR 配對'])
def test_reported_device_labels_have_complete_glyph_sets(label):
  assert {ord(c) for c in label} <= generated_codepoints()
