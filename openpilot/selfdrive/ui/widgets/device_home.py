import pyray as rl

from openpilot.selfdrive.ui.home_surface import home_scene
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.lib.multilang import multilang, tr
from openpilot.system.ui.widgets.label import gui_label


class DeviceHome:
  def __init__(self, compact):
    self.compact = compact
    self.scene_key = self.scene = None
    self.hits = {}
    self.pressed = None

  def render(self, rect, branch, address, experimental=False):
    key = (branch, address, multilang.language, experimental)
    if self.scene_key != key:
      self.scene = home_scene(self.compact, branch, address, tr, experimental)
      self.scene_key = key
    w, h, boxes, labels, actions = self.scene
    sx, sy = rect.width / w, rect.height / h
    def bounds(x, y, width, height):
      return rl.Rectangle(rect.x + x*sx, rect.y + y*sy, width*sx, height*sy)
    for x, y, width, height, color in boxes:
      rl.draw_rectangle_rec(bounds(x, y, width, height), rl.get_color(int(color[1:]+"ff", 16)))
    for x, y, width, height, text, size, color, bold in labels:
      gui_label(bounds(x, y, width, height), text, max(1, int(size*min(sx, sy))), rl.get_color(int(color[1:]+"ff", 16)),
                font_weight=FontWeight.BOLD if bold else FontWeight.NORMAL)
    self.hits = {key: bounds(*box) for key, box in actions.items()}

  def hit(self, pos):
    return next((key for key, rect in self.hits.items() if rl.check_collision_point_rec(pos, rect)), None)
