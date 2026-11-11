from openpilot.system.ui.lib.branding import display_text
import pyray as rl
from openpilot.system.ui.lib.application import font_fallback, text_size_scale

_cache: dict[int, rl.Vector2] = {}


def measure_text_cached(font: rl.Font, text: str, font_size: int, spacing: float = 0) -> rl.Vector2:
  """Caches text measurements to avoid redundant calculations."""
  text = display_text(text)
  font = font_fallback(font, text)
  scale = text_size_scale(text)
  spacing = round(spacing, 4)
  key = hash((font.texture.id, text, font_size, spacing, scale))
  if key in _cache:
    return _cache[key]

  result = rl.measure_text_ex(font, text, font_size * scale, spacing)  # noqa: TID251

  _cache[key] = result
  return result
