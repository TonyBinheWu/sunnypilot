"""The optional comma body face on the device's rightmost page."""
import math
import time

import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets import Widget


# Lit dots in the three distinct eye frames of selfdrive/assets/body/awake.gif.
OPEN = ((1, 2), (0, 1, 2, 3), (0, 1, 2, 3), (1, 2))
HALF = ((), (), (0, 1, 2, 3), (1, 2))
CLOSED = ((), (), (0, 3), (1, 2))


def face_speed(state, now):
  sm = state.sm
  if (not state.started or not sm.alive["carState"] or not sm.valid["carState"] or
      sm.recv_frame["carState"] < state.started_frame or not 0 <= now - sm.recv_time["carState"] <= 0.5):
    return 0.0
  speed = sm["carState"].vEgo
  return max(0.0, speed) if math.isfinite(speed) else 0.0


def draw_eyes(rect, speed, now):
  # Scale continuously from resting to the most focused pose at 100 km/h.
  focus = min(speed / (100 / 3.6), 1.0)
  pitch = min(rect.width / 13.0, rect.height / 6.0)
  phase = now % 4.8
  rows = CLOSED if phase < 0.10 else HALF if phase < 0.20 or phase > 4.70 else OPEN
  glance = math.sin(now * 0.85) * 0.30 * (1 - focus)
  for side in (-1, 1):
    cx = rect.x + rect.width / 2 + (side * 3.6 + glance) * pitch
    cy = rect.y + rect.height / 2
    for row, columns in enumerate(rows):
      for column in columns:
        x = column - 1.5
        y = (row - 1.5) * (1 - 0.35 * focus) - side * x * 0.20 * focus
        rl.draw_ellipse(round(cx + x * pitch), round(cy + y * pitch),
                        pitch * 0.36, pitch * 0.36 * (1 - 0.35 * focus), rl.WHITE)


def render_body_eyes(rect, render_alert=None):
  rl.draw_rectangle_rec(rect, rl.BLACK)
  if ui_state.started and render_alert is not None and render_alert(rect):
    return
  now = time.monotonic()
  draw_eyes(rect, face_speed(ui_state, now), now)


def horizontal_swipe(start, end, width):
  """Return the finger's direction for a deliberate horizontal page gesture."""
  if start is None:
    return 0
  dx = end.x - start.x
  if abs(dx) < max(48, width * 0.15) or abs(dx) < 2 * abs(end.y - start.y):
    return 0
  return 1 if dx > 0 else -1


def is_tap(start, end):
  return start is not None and max(abs(start.x - end.x), abs(start.y - end.y)) < 30


class BodyEyesPage(Widget):
  def __init__(self):
    super().__init__()
    self._press_start = None

  def _render(self, rect):
    render_body_eyes(rect)

  def _handle_mouse_press(self, pos):
    self._press_start = pos

  def _handle_mouse_release(self, pos):
    start, self._press_start = self._press_start, None
    if is_tap(start, pos) or horizontal_swipe(start, pos, self.rect.width) == 1:
      super()._handle_mouse_release(pos)
