"""Presentation and touch geometry for the two native device screens."""
import pyray as rl

from openpilot.system.ui.lib.application import FontWeight, font_fallback, gui_app
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget

BASE = rl.Color(22, 30, 27, 255)
BAR = rl.Color(28, 38, 34, 255)
TILE = rl.Color(39, 52, 45, 255)
SELECTED = rl.Color(48, 74, 59, 255)
INK = rl.Color(237, 244, 240, 255)
MINT = rl.Color(176, 235, 197, 255)
VIEW_NAMES = ("3D scene", "Camera", "3D model")
SECTION_ICONS = {
  "device": "settings/device_icon.png", "display": "settings.png", "network": "settings/network/wifi_strength_full.png",
  "egpu": "settings/developer_icon.png", "camera": "settings/device/cameras.png", "software": "settings/device/power.png",
}


def caption(rect, text, size, color=INK, *, centered=False):
  font = font_fallback(gui_app.font(FontWeight.MEDIUM), text)
  width = measure_text_cached(font, text, size).x
  if width > rect.width - 8:
    size = max(9, int(size * (rect.width - 8) / max(width, 1)))
    width = measure_text_cached(font, text, size).x
  x = rect.x + ((rect.width - width) / 2 if centered else 4)
  rl.draw_text_ex(font, text, rl.Vector2(x, rect.y + (rect.height - size) / 2), size, 0, color)


def tile(rect, text, size, selected=False):
  rl.draw_rectangle_rounded(rect, .16, 4, SELECTED if selected else TILE)
  caption(rect, text, size, MINT if selected else INK, centered=True)


def section_label(box, key, title, font_size, color):
  path = SECTION_ICONS.get(key)
  if path:
    side = min(box.height * .55, font_size * 1.15)
    texture = gui_app.texture("icons_mici/" + path, round(side), round(side))
    rl.draw_texture_pro(texture, rl.Rectangle(0, 0, texture.width, texture.height),
                        rl.Rectangle(box.x+4, box.y+(box.height-side)/2, side, side), rl.Vector2(0, 0), 0, MINT)
    offset = side + 12
    box = rl.Rectangle(box.x+offset, box.y, box.width-offset, box.height)
  caption(box, title, font_size, color)


def grid_cells(rect, count, columns=2, gap=6):
  rows = (count + columns - 1) // columns
  w = (rect.width - (columns - 1) * gap) / columns
  h = (rect.height - (rows - 1) * gap) / rows
  return [rl.Rectangle(rect.x + (i % columns) * (w + gap), rect.y + (i // columns) * (h + gap), w, h) for i in range(count)]


class TouchMenu(Widget):
  def __init__(self):
    super().__init__()
    self.targets = {}
    self._pressed_target = None

  def _hit(self, pos):
    return next((key for key, box in self.targets.items() if rl.check_collision_point_rec(pos, box)), None)

  def _handle_mouse_press(self, pos):
    self._pressed_target = self._hit(pos)

  def _handle_mouse_release(self, pos):
    key, self._pressed_target = self._pressed_target, None
    if key is not None and key == self._hit(pos):
      self.activate(key)

  def hide_event(self):
    self._pressed_target = None
    super().hide_event()


class DisplaySettings(TouchMenu):
  rows = (
    ("IsMetric", "Speed units", ("mph", "km/h")),
    ("DrivingSceneView", "Driving view", VIEW_NAMES),
    ("DeviceSceneEco", "Road updates", ("20 Hz", "12 Hz")),
    ("DeviceSceneDim", "Road brightness", ("Standard", "Dim")),
  )

  def __init__(self, state):
    super().__init__()
    self.state = state
    self.values = {}

  def show_event(self):
    super().show_event()
    for key, _, _ in self.rows:
      self.values[key] = self.state.params.get(key, return_default=True)

  def activate(self, choice):
    key, index = choice
    if not self.state.is_offroad():
      return
    if key == "IsMetric":
      from openpilot.common.params import UnknownKeyName
      try:
        if self.state.params.get_bool("IsMetricLock"):
          return
      except UnknownKeyName:
        pass
    if key == "DrivingSceneView":
      self.state.params.put(key, index)
    else:
      self.state.params.put_bool(key, bool(index))
    self.values[key] = index

  def _render(self, rect):
    small = rect.width < 800
    gap = 4 if small else 14
    self.targets.clear()
    for (key, title, options), row in zip(self.rows, grid_cells(rect, len(self.rows), 1, gap), strict=True):
      width = row.width * (.33 if small else .39)
      caption(rl.Rectangle(row.x, row.y, width, row.height), tr(title), 16 if small else 44)
      choices = rl.Rectangle(row.x + width, row.y, row.width - width, row.height)
      value = self.values.get(key)
      if key == "DrivingSceneView" and value == -1:
        from openpilot.selfdrive.ui.layout_profile import device_layout, large_display_layout
        style = device_layout("c4") if small else large_display_layout()
        value = 0 if style["scene_style"] else 1
      for i, (label, box) in enumerate(zip(options, grid_cells(choices, len(options), len(options), gap), strict=True)):
        tile(box, tr(label), 15 if small else 39, i == value)
        self.targets[key, i] = box


class DrivingViewSelector:
  def __init__(self, compact):
    self.compact = compact
    self.boxes = []
    self.press = None
    self.cancelled = False
    self.active_view = 0

  def draw(self, rect, view, visible):
    self.boxes.clear()
    if not visible:
      self.cancelled = True
      return
    self.active_view = view
    w, h, margin = (112, 42, 12) if self.compact else (min(620, rect.width*.42), 76, 30)
    area = rl.Rectangle(rect.x+rect.width-w-margin, rect.y+rect.height-h-margin, w, h)
    self.boxes = grid_cells(area, 1 if self.compact else 3, 1 if self.compact else 3)
    for i, box in enumerate(self.boxes):
      mode = view if self.compact else i
      tile(box, tr(VIEW_NAMES[mode]) + (" ›" if self.compact else ""), 17 if self.compact else 35, mode == view)

  def begin(self, pos):
    self.cancelled = False
    self.press = next(((i, pos.x, pos.y) for i, box in enumerate(self.boxes) if rl.check_collision_point_rec(pos, box)), None)
    return self.press is not None

  def finish(self, pos, state, allowed):
    if self.press is None:
      return False
    i, x, y = self.press
    self.press = None
    same_box = i < len(self.boxes) and rl.check_collision_point_rec(pos, self.boxes[i])
    tap = max(abs(x - pos.x), abs(y - pos.y)) < (14 if self.compact else 30)
    if allowed and state.started and same_box and tap and not self.cancelled:
      view = (self.active_view+1) % 3 if self.compact else i
      state.params.put_nonblocking("DrivingSceneView", view)
      state.driving_scene_view = view
    return True
