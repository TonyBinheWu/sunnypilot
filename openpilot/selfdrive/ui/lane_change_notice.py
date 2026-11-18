"""Bounded two-line lane-change notice below the normal driving header."""
import time

import pyray as rl

from openpilot.common.lane_change_notice import TITLES, fresh_notice
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.lib.text_measure import measure_text_cached

# Static gettext extraction for the keys shared with the web presentation.
NATIVE_MESSAGES = (
  tr_noop('Model anticipates a left lane change'), tr_noop('Model anticipates a right lane change'),
  tr_noop('Prepare to change left'), tr_noop('Prepare to change right'),
  tr_noop('Left lane-change procedure active'), tr_noop('Right lane-change procedure active'),
  tr_noop('Left exit ahead'), tr_noop('Right exit ahead'),
  tr_noop('Left lane change completed'), tr_noop('Right lane change completed'),
  tr_noop('Left lane change cancelled'), tr_noop('Right lane change cancelled'),
  tr_noop('Left lane change ended; completion unconfirmed'), tr_noop('Right lane change ended; completion unconfirmed'),
  tr_noop('Keep watching the road and surrounding traffic'),
  tr_noop('Check your lane; operate the indicator yourself if needed'),
  tr_noop('Check traffic and operate the indicator yourself'), tr_noop('Indicator on; check surrounding traffic'),
)


def draw_lane_change_notice(sm, rect, font):
  value = fresh_notice(sm, time.monotonic())
  if value is None:
    return False
  kind, direction = value
  title = tr(TITLES[value])
  cs = sm['carState']
  lamp_on = cs.leftBlinker if direction == 'left' else cs.rightBlinker
  if kind in ('completed', 'cancelled', 'unverified'):
    detail = tr('Keep watching the road and surrounding traffic')
  elif kind == 'exit':
    detail = tr('Check your lane; operate the indicator yourself if needed')
  else:
    detail = tr('Check traffic and operate the indicator yourself') if not lamp_on else tr('Indicator on; check surrounding traffic')
  width = min(760., rect.width * .62)
  size = min(36., max(20., rect.width / 48.))
  x, y = rect.x + (rect.width - width) / 2, rect.y + rect.height * .16
  color = rl.Color(90, 220, 150, 255) if kind == 'completed' else rl.Color(255, 203, 93, 255)
  rl.draw_rectangle(int(x), int(y), int(width), int(size * 2.9), rl.Color(10, 18, 28, 225))
  for i, text in enumerate((title, detail)):
    measured = measure_text_cached(font, text, size).x
    fitted = min(size, size * (width - 24) / max(1., measured))
    rl.draw_text_ex(font, text, rl.Vector2(x + 12, y + 6 + i * size * 1.3), fitted, 0, color if i == 0 else rl.WHITE)
  return True
