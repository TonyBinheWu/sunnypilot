"""Bake the real cold-start font on CPU; no display or generated atlas needed."""
import ast
from enum import StrEnum
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = ROOT / 'openpilot/selfdrive/assets/fonts'


def source_repertoire():
  path = ROOT / 'openpilot/system/ui/lib/application.py'
  tree = ast.parse(path.read_text(encoding='utf-8'))
  weights = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'FontWeight')
  app = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'GuiApplication')
  method = next(n for n in app.body if isinstance(n, ast.FunctionDef) and n.name == '_font_codepoints')
  scope = {'StrEnum': StrEnum, 'BIG_UI': False, 'FONT_DIR': FONT_DIR}
  exec(compile(ast.Module(body=[weights, method], type_ignores=[]), str(path), 'exec'), scope)
  return scope['_font_codepoints'](None, scope['FontWeight'].DISPLAY)


def test_cold_start_repertoire_retains_the_shipped_multilingual_ui():
  pytest.importorskip('pyray')
  spec = importlib.util.spec_from_file_location('bootstrap_font_process', FONT_DIR / 'process.py')
  process = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(process)
  _, multilingual = process._char_sets()
  assert set(multilingual) <= set(source_repertoire())


def test_c4_cold_start_font_fits_an_8192_atlas():
  # This exercises real stb font loading/packing on both the original AGNOS
  # Raylib 5.5 API and the target Raylib 6 API. A mere import test missed it.
  rl = pytest.importorskip('raylib')
  points = source_repertoire()
  data = (FONT_DIR / 'KaiGenGothicKR-Bold.ttf').read_bytes()
  buffer = rl.ffi.new('unsigned char[]', data)
  codepoints = rl.ffi.new('int[]', points)
  count = rl.ffi.new('int *', len(points))
  args = [rl.ffi.cast('unsigned char *', buffer), len(data), 48, codepoints, len(points), 0]
  if len(rl.ffi.typeof(rl.LoadFontData).args) == 7:
    args.append(count)
  glyphs = rl.LoadFontData(*args)
  assert glyphs != rl.ffi.NULL
  image = None
  rects = rl.ffi.new('Rectangle **')
  try:
    image = rl.GenImageFontAtlas(glyphs, rects, count[0], 48, 4, 0)
    assert 0 < image.width <= 8192
    assert 0 < image.height <= 8192
    assert image.data != rl.ffi.NULL
  finally:
    if image is not None:
      rl.UnloadImage(image)
    if rects[0] != rl.ffi.NULL:
      rl.MemFree(rects[0])
    rl.UnloadFontData(glyphs, count[0])
