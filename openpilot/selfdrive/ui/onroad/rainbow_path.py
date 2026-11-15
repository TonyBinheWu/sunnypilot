"""SP-style display-only animated rainbow, using the existing polygon shader.

Derived from sunnypilot's RainbowPath (MIT).
Copyright (c) 2021-, Haibin Wen, sunnypilot, and other contributors.
See LICENSE.md for the MIT license. No path geometry or controls are changed.
"""
import colorsys
import math

import pyray as rl

from openpilot.system.ui.lib.shader_polygon import Gradient, draw_polygon


class RainbowPath:
  def __init__(self):
    self._phase = None
    self._gradient = None

  def gradient(self, now):
    # Reuse the gradient within each animation phase; no extra timer or render loop.
    phase = int((now * 50.0) % 360.0) if math.isfinite(now) else 0
    if phase != self._phase:
      colors = []
      for i in range(8):
        t = i / 7
        rgb = colorsys.hls_to_rgb(((phase + t * 360) % 360) / 360, .6, .9)
        colors.append(rl.Color(*(int(v * 255) for v in rgb), int(.8 * (1 - .3 * t) * 255)))
      self._gradient = Gradient(start=(0.0, 1.0), end=(0.0, 0.0), colors=colors, stops=[i / 7 for i in range(8)])
      self._phase = phase
    return self._gradient

  def draw(self, rect, points, now):
    if len(points) >= 3:
      draw_polygon(rect, points, gradient=self.gradient(now))
