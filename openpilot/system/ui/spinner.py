#!/usr/bin/env python3
import sys
from functools import lru_cache

import pyray as rl

from openpilot.common.network_info import label_with_port, start_ip_monitor
from openpilot.system.ui.boot_status import BootStatus, StatusInput, fit_lines
from openpilot.system.ui.lib.application import ASSETS_DIR, FontWeight, gui_app
from openpilot.system.ui.lib.multilang import multilang, tr

RECOVERY_PORT = 6999
BG = (19, 29, 26, 255)
INK = (238, 245, 237, 255)
MUTED = (163, 184, 171, 255)
MINT = (173, 235, 192, 255)
TRACK = (53, 73, 63, 255)


def road_point(t):
  # Perspective study for the splash illustration, in local artwork coordinates.
  center = .58 - .34*t + .30*t*t
  return center, .48 + .52*t, .012 + .44*t**1.45


class RoadIllustration:
  def __init__(self, rect):
    self.rect = rect
    def ribbon(levels, left, right):
      points = []
      for t in levels:
        center, y, half = road_point(t)
        points.extend((self.point(center+right*half, y), self.point(center+left*half, y)))
      return points
    levels = [i/22 for i in range(23)]
    self.strips = []
    for heights, color in [((.53,.46,.48,.40,.32,.39,.42,.37,.46), (83, 125, 102, 255)),
                           ((.56,.51,.47,.50,.52,.47,.44,.49,.45), (53, 91, 73, 255))]:
      points = []
      for i, y in enumerate(heights):
        x = i / (len(heights)-1)
        points.extend((self.point(x, y), self.point(x, 1.)))
      self.strips.append((points, color))
    self.strips.extend([(ribbon(levels, -1., 1.), (34, 56, 50, 255)),
                        (ribbon(levels, -.98, -.95), (144, 184, 156, 255)),
                        (ribbon(levels, .95, .98), (145, 185, 156, 255))])

  def point(self, x, y):
    r = self.rect
    return rl.Vector2(r.x + r.width*x, r.y + r.height*y)

  def draw(self, phase):
    r = self.rect
    rl.draw_rectangle_gradient_v(int(r.x), int(r.y), int(r.width), int(r.height), (42, 77, 66, 255), (161, 193, 153, 255))
    rl.draw_circle_v(self.point(.65,.33), min(r.width,r.height)*.112, (249, 189, 131, 255))
    for vertices, color in self.strips:
      rl.draw_triangle_strip(vertices, len(vertices), color)
    for i in range(7):
      a, b = (i + phase) / 7, min(1., (i + phase + .46)/7)
      x1, y1, _ = road_point(a*a)
      x2, y2, _ = road_point(b*b)
      rl.draw_line_ex(self.point(x1,y1), self.point(x2,y2), max(1., r.width*(.002+.012*a*a)), MINT)


class Spinner:
  def __init__(self):
    self.status = BootStatus()
    self.size = self.art = None
    self.font = gui_app.font(FontWeight.PRETENDARD)
    self.localized = None
    if multilang.language in ("zh-CHT", "zh-CHS", "ja", "ko"):
      # A pre-baked small atlas is available even on a clean checkout.
      self.localized = rl.load_font((ASSETS_DIR / "boot/labels.fnt").as_posix())
      rl.set_texture_filter(self.localized.texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
    self.lines = lru_cache(maxsize=16)(self._lines)
    start_ip_monitor()

  def close(self):
    if self.localized is not None:
      if rl.is_window_ready():
        rl.unload_font(self.localized)
      self.localized = None
    self.lines.cache_clear()

  def font_for(self, text):
    return self.localized if self.localized is not None and not text.isascii() else self.font

  def _lines(self, text, width, size):
    font = self.font_for(text)
    return fit_lines(text, width, lambda part: rl.measure_text_ex(font, part, size, 0).x)  # noqa: TID251 -- native bitmap sizes

  def draw_text(self, text, x, y, size, color):
    # Use logical pixel sizes for both measurement and drawing on each device.
    draw = getattr(rl, "_orig_draw_text_ex", rl.draw_text_ex)
    draw(self.font_for(text), text, rl.Vector2(x,y), size, 0, color)

  def render(self, width, height, elapsed):
    compact = width < 800
    scale = min(width/536, height/240)
    if self.size != (width, height):
      self.size = (width, height)
      art = rl.Rectangle(0, 0, int(width*.34), height) if compact else rl.Rectangle(
        int(width*.046), int(height*.09), int(width*.40), int(height*.82))
      self.art = RoadIllustration(art)
    rl.draw_rectangle(0, 0, width, height, BG)
    phase = (elapsed / 1.65) % 1.
    self.art.draw(phase)
    x = round(width * (.382 if compact else .51))
    right = width - round(width*(.04 if compact else .065))
    span = right-x
    self.draw_text("carrotpilot", x, height*.13, (41 if compact else 43)*scale, INK)
    detail = tr(self.status.detail) if self.status.detail else ""
    if self.status.context:
      detail = self.status.context + ("  /  "+detail if detail else "")
    if not detail:
      detail = tr("Starting up" if self.status.progress is None else "Building software")
    size = (20 if compact else 17)*scale
    for i, line in enumerate(self.lines(detail, span, size)):
      self.draw_text(line, x, height*.405+i*size*1.15, size, INK)
    y, h = round(height*.685), max(3,round(3.5*scale))
    bar_width = span
    if self.status.progress is not None:
      label = f"{self.status.progress}%"
      label_size = 17*scale
      label_width = rl.measure_text_ex(self.font, label, label_size, 0).x  # noqa: TID251
      bar_width -= round(53*scale)
      self.draw_text(label, right-label_width, y-label_size*.43, label_size, MINT)
    rl.draw_rectangle(x, y, bar_width, h, TRACK)
    if self.status.progress is None:
      segment = round(bar_width*.20)
      left = round((bar_width+segment)*phase)-segment
      start, end = max(0,left), min(bar_width,left+segment)
    else:
      start, end = 0, round(bar_width*self.status.progress/100)
    if end > start:
      rl.draw_rectangle(x+start, y, end-start, h, MINT)

    address = label_with_port(RECOVERY_PORT)
    y = height*.845
    label = tr("Recovery")
    size = (17 if compact else 14)*scale
    self.draw_text(label, x, y, size, MUTED)
    value = tr("Offline") if address == "no network" else address
    text_width = rl.measure_text_ex(self.font_for(value), value, size, 0).x  # noqa: TID251
    self.draw_text(value, right-text_width, y, size, INK)


def main():
  gui_app.init_window("Spinner", font_weights=(FontWeight.NORMAL, FontWeight.PRETENDARD))
  gui_app.set_display_rate(20)
  spinner = Spinner()
  stream = StatusInput(sys.stdin.fileno())
  try:
    for visible in gui_app.render():
      stream.poll(spinner.status)
      if visible:
        spinner.render(gui_app.width, gui_app.height, rl.get_time())
  finally:
    spinner.close()


if __name__ == "__main__":
  main()
