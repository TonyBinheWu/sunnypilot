"""Regression checks for dynamic CJK fallback font cache (no hardware required)."""
import ast
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).resolve().parents[2] / "openpilot/system/ui/lib/application.py"


class FakeRaylib:
  def __init__(self):
    self.loads = []
    self.unloads = []
    self.Font = object
    self.ffi = SimpleNamespace(new=lambda signature, values: list(values), cast=lambda signature, values: values)
    self.TextureFilter = SimpleNamespace(TEXTURE_FILTER_TRILINEAR=1, TEXTURE_FILTER_BILINEAR=2)

  def load_font_ex(self, filename, size, codepoints, length):
    points = set(codepoints)
    self.loads.append((str(filename), points))
    # The primary font is a subset. Unifont also intentionally lacks an emoji.
    if "unifont" in str(filename):
      supported = points - {0x1F6A8}
    else:
      supported = points & {ord(c) for c in "常用字"}
    return SimpleNamespace(texture=SimpleNamespace(id=len(self.loads)), glyphCount=len(supported),
                           glyphs=[SimpleNamespace(value=point) for point in supported])

  def gen_texture_mipmaps(self, texture):
    return None

  def set_texture_filter(self, texture, filter_mode):
    return None

  def unload_font(self, font):
    self.unloads.append(font)


class FakeTranslations:
  def joinpath(self, path):
    return SimpleNamespace(read_text=lambda encoding: "常用字系統錯誤繁體")


def extract_method():
  tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GuiApplication")
  method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "fallback_font")
  return compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), "exec")


class TestFallbackAtlas(unittest.TestCase):
  def setUp(self):
    self.rl = FakeRaylib()
    self.language = SimpleNamespace(language="zh-CHT")
    self.warnings = []
    env = {
      "rl": self.rl, "multilang": self.language, "cloudlog": SimpleNamespace(warning=self.warnings.append),
      "TRANSLATIONS_DIR": FakeTranslations(), "FONT_DIR": Path("/fake/fonts"),
      "NOTO_FONTS": {"zh-CHT": "SourceHanSansTC-Regular.otf", "ja": "NotoSansCJKjp-Regular.otf"},
      "EXTRA_FONT_CHARS": "◀▶", "as_file": nullcontext,
    }
    exec(extract_method(), env)
    self.fallback = env["fallback_font"]
    self.app = SimpleNamespace(_fallback_fonts={}, _fallback_codepoints={},
                               _fallback_unavailable_codepoints={})

  def test_primary_cjk_font_remains_available(self):
    font = self.fallback(self.app, "常用字")
    self.assertEqual(font, self.app._fallback_fonts["zh-CHT"])
    self.assertEqual(len(self.rl.loads), 1)

  def test_missing_glyph_does_not_reload_or_unload_each_frame(self):
    first = self.fallback(self.app, "系統錯誤🚨")
    self.assertIs(first, self.app._fallback_fonts["zh-CHT:unifont"])
    for _ in range(100):
      self.assertIs(first, self.fallback(self.app, "系統錯誤🚨"))
    # One primary atlas and one stable unifont atlas; never unload mid-draw.
    self.assertEqual(len(self.rl.loads), 2)
    self.assertEqual(len(self.rl.unloads), 0)
    self.assertEqual(len(self.warnings), 1)
    self.assertIn("1 new glyphs", self.warnings[0])

  def test_new_dynamic_glyphs_do_not_rebuild_atlas(self):
    first = self.fallback(self.app, "系統錯誤🚨")
    for _ in range(100):
      self.assertIs(first, self.fallback(self.app, "系統錯誤🛸"))
    self.assertEqual(len(self.rl.loads), 2)
    self.assertEqual(len(self.rl.unloads), 0)
    self.assertEqual(len(self.warnings), 2)

  def test_separate_language_cache(self):
    self.fallback(self.app, "系統錯誤🚨")
    self.language.language = "ja"
    self.fallback(self.app, "新")
    self.assertEqual(len(self.rl.loads), 4)
    self.assertIn("ja:unifont", self.app._fallback_fonts)


if __name__ == "__main__":
  unittest.main(verbosity=2)
