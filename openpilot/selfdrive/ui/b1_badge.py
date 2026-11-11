"""Persistent B1 link indicator on the C3 and C4 home and driving screens."""
from openpilot.system.ui.lib.multilang import tr_noop
import json
from pathlib import Path
import time

ENROLLED = Path('/data/carrot/b1-monitor.json')
STATUS = Path('/dev/shm/carrot-b1-link.json')
LABELS = {
  'updating': (tr_noop('S3 · Updating'), (96, 218, 243)),
  'offline': (tr_noop('S3 · Waiting for connection'), (170, 178, 188)),
  'auth': (tr_noop('S3 · Authenticating'), (255, 197, 89)),
  'missing': (tr_noop('S3 · Waiting for CAN'), (202, 147, 255)),
  'ready': (tr_noop('S3 · CAN connected'), (96, 232, 162)),
  'waiting': (tr_noop('S3 · CAN connected'), (96, 232, 162)),
  'sending': (tr_noop('S3 · Sending'), (96, 218, 243)),
  'driver_override': (tr_noop('S3 · Stock lever priority'), (255, 197, 89)),
  'error': (tr_noop('S3 · CAN error'), (252, 128, 110)),
}


def status(now, enrolled=ENROLLED, path=STATUS):
  if not enrolled.is_file():
    return None
  try:
    with path.open('rb') as stream:
      record = json.loads(stream.read(256))
    if 0 <= now-record['time'] < 2 and record['state'] in LABELS:
      return record['state']
  except (OSError, KeyError, ValueError, TypeError):
    pass
  return 'offline'


_next = 0.
_state = None


def draw(rect, *, top=None, right_margin=None):
  global _next, _state
  now = time.monotonic()
  if now >= _next:
    _state = status(now)
    _next = now + .35
  if _state is None:
    return
  from openpilot.system.ui.lib.multilang import tr
  import pyray as rl
  from openpilot.system.ui.lib.application import FontWeight, gui_app
  label, rgb = LABELS[_state]
  size = 24 if rect.width >= 1200 else 16
  width = size*8
  x, y = rect.x + rect.width*.72 - width/2, rect.y + size*.55
  if top is not None:
    y = rect.y + top
  if right_margin is not None:
    x = rect.x + rect.width - right_margin - width
  rl.draw_rectangle_rounded(rl.Rectangle(x, y, width, size*1.55), .7, 8, rl.Color(10, 18, 25, 220))
  rl.draw_circle(int(x+size*.62), int(y+size*.77), size*.19, rl.Color(*rgb, 255))
  rl.draw_text_ex(gui_app.font(FontWeight.DISPLAY), tr(label), rl.Vector2(x+size*1.05, y+size*.24), size, 0, rl.WHITE)
