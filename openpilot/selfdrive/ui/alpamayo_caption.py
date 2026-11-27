"""Render the admitted plan's explanation. No caption data is used by controls."""
from functools import lru_cache
from math import ceil
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
    return '一般行駛' if traditional else '常规行驶' if chinese else 'Nominal driving'
  if chinese and sm.valid['alpamayoSubtitle'] and sm.recv_frame['alpamayoSubtitle'] >= started_frame:
    sub = sm['alpamayoSubtitle']
    if 0 < sub.queryMonoTime <= query and sub.original == raw:
      translated = sub.traditional if traditional else sub.simplified
      if translated:
        return translated
  return raw


@lru_cache(maxsize=6)
def subtitle_font(size):
  from PIL import ImageFont
  return ImageFont.truetype(str(FONT), size)


def render_caption(text, width, size):
  from PIL import Image, ImageDraw
  # The fixed UI glyph atlas contains only UI vocabulary; rasterize free text with the full source font.
  font = subtitle_font(size)
  padding = size//3
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
  lines = [line.rstrip() for line in lines]
  text_width = ceil(max(font.getlength(line) for line in lines))
  line_height = sum(font.getmetrics())
  inset_y = max(2, size//8)
  image = Image.new('RGBA', (min(width, text_width+2*padding), len(lines)*line_height+2*inset_y), (12, 19, 27, 220))
  draw = ImageDraw.Draw(image)
  for i, line in enumerate(lines):
    draw.text((padding, inset_y+i*line_height), line, font=font, fill='white')
  return image


class AlpamayoCaption:
  def __init__(self):
    self.key = self.texture = self.source = None

  def draw(self, rect, ui):
    import pyray as rl
    from openpilot.system.ui.lib.multilang import multilang
    value = caption(ui.sm, time.monotonic_ns(), multilang.language, ui.started_frame)
    if value is None:
      return
    width, size = int(rect.width*.55), max(14, min(30, int(rect.width/46)))
    key = (value, width, size)
    if key != self.key:
      image = render_caption(*key)
      if self.texture is None or self.texture.width != width or self.texture.height < image.height:
        self.close()
        blank = rl.gen_image_color(width, image.height, rl.BLANK)
        self.texture = rl.load_texture_from_image(blank)
        rl.unload_image(blank)
      pixels = image.tobytes()
      self.source = rl.Rectangle(0, 0, image.width, image.height)
      rl.update_texture_rec(self.texture, self.source, rl.ffi.cast('void *', rl.ffi.from_buffer(pixels)))
      self.key = key
    y = min(rect.height*.76, rect.height-self.source.height-4)
    pos = rl.Vector2(int(rect.x+(rect.width-self.source.width)/2), int(rect.y+y))
    rl.draw_texture_rec(self.texture, self.source, pos, rl.WHITE)

  def close(self):
    if self.texture is not None:
      import pyray as rl
      rl.unload_texture(self.texture)
      self.texture = self.key = self.source = None
