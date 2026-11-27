"""Render the admitted plan's explanation. No caption data is used by controls."""
from functools import lru_cache
from pathlib import Path
import re
import time

FONT = Path(__file__).resolve().parents[1]/'assets/fonts/unifont.otf'


def caption(sm, now_ns, language, started_frame):
  if (not sm.valid['modelV2'] or sm.recv_frame['modelV2'] < started_frame or
      not 0 <= now_ns-sm.logMonoTime['modelV2'] < 250_000_000):
    return None
  model = sm['modelV2']
  query, raw = model.alpamayoQueryMonoTime, model.alpamayoReasoning.strip()
  if not query or not raw or not 0 <= now_ns-query < 1_500_000_000:
    return None
  language = language.removeprefix('main_')
  traditional = language == 'zh-CHT'
  chinese = traditional or language == 'zh-CHS'
  if raw == '<NOMINAL>':
    return ('lat2v 模型判讀', '一般行駛') if traditional else (
      ('lat2v 模型判断', '常规行驶') if chinese else ('lat2v model', 'Nominal driving'))
  if chinese and sm.valid['alpamayoSubtitle'] and sm.recv_frame['alpamayoSubtitle'] >= started_frame:
    sub = sm['alpamayoSubtitle']
    if 0 < sub.queryMonoTime <= query and sub.original == raw:
      translated = sub.traditional if traditional else sub.simplified
      if translated:
        return ('lat2v 模型判讀 · 機器翻譯' if traditional else 'lat2v 模型判断 · 机器翻译', translated)
  return ('lat2v 模型判讀 · 原文' if traditional else 'lat2v 模型判断 · 原文' if chinese else 'lat2v model', raw)


@lru_cache(maxsize=6)
def subtitle_font(size):
  from PIL import ImageFont
  return ImageFont.truetype(str(FONT), size)


def render_caption(title, text, width, size):
  from PIL import Image, ImageDraw
  # The fixed UI glyph atlas contains only UI vocabulary; rasterize free text with the full source font.
  font = subtitle_font(size)
  padding = size//2
  image = Image.new('RGBA', (width, size*4), (12, 19, 27, 220))
  draw = ImageDraw.Draw(image)
  draw.text((padding, 2), title, font=subtitle_font(max(12, size-2)), fill=(170, 216, 236))
  lines = ['']
  words = re.findall(r"[A-Za-z0-9'-]+|[^\s]|\s+", ' '.join(text[:512].split()))
  tokens = []
  for word in words:
    if font.getlength(word) > width-2*padding:
      tokens.extend(word)
    else:
      tokens.append(word)
  for word in tokens:
    if font.getlength(lines[-1]+word) <= width-2*padding:
      lines[-1] += word
    elif len(lines) < 2:
      lines.append(word.lstrip())
    else:
      while lines[-1] and font.getlength(lines[-1]+'…') > width-2*padding:
        lines[-1] = lines[-1][:-1]
      lines[-1] = lines[-1].rstrip()+'…'
      break
  for i, line in enumerate(lines):
    draw.text((padding, size*(1.25+i*1.18)), line, font=font, fill='white')
  return image


class AlpamayoCaption:
  def __init__(self):
    self.key = self.texture = None

  def draw(self, rect, ui):
    import pyray as rl
    from openpilot.system.ui.lib.multilang import multilang
    value = caption(ui.sm, time.monotonic_ns(), multilang.language, ui.started_frame)
    if value is None:
      return
    width, size = int(rect.width*.55), max(14, min(30, int(rect.width/46)))
    key = (*value, width, size)
    if key != self.key:
      image = render_caption(*key)
      if self.texture is None or self.texture.width != width or self.texture.height != image.height:
        self.close()
        blank = rl.gen_image_color(width, image.height, rl.BLANK)
        self.texture = rl.load_texture_from_image(blank)
        rl.unload_image(blank)
      pixels = image.tobytes()
      rl.update_texture(self.texture, rl.ffi.cast('void *', rl.ffi.from_buffer(pixels)))
      self.key = key
    y = min(rect.height*.76, rect.height-self.texture.height-4)
    rl.draw_texture(self.texture, int(rect.x+(rect.width-width)/2), int(rect.y+y), rl.WHITE)

  def close(self):
    if self.texture is not None:
      import pyray as rl
      rl.unload_texture(self.texture)
      self.texture = self.key = None
