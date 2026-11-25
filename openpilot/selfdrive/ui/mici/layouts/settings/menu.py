import pyray as rl

from openpilot.selfdrive.ui.device_design import BASE, INK, MINT, SELECTED, TILE, SECTION_ICONS, DisplaySettings, caption, grid_cells
from openpilot.selfdrive.ui.layout_profile import device_layout
from openpilot.selfdrive.ui.mici.layouts.settings.navigation import DeviceTouchMenu, HEADER_HEIGHT, SettingsToolbar
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.lib.application import gui_app


class DisplayPicker(DisplaySettings, DeviceTouchMenu):
  def __init__(self, state, close):
    super().__init__(state)
    self.row = None
    self.close = close

  def title(self):
    return tr("Display & units" if self.row is None else self.rows[self.row][1])

  def back(self):
    if self.row is None:
      self.close()
    else:
      self.row = None

  def activate(self, key):
    if self.row is None:
      self.row = key
    else:
      super().activate((self.rows[self.row][0], key))
      self.row = None

  def _render(self, rect):
    self.targets.clear()
    if self.row is None:
      labels = [tr(title) for _, title, _ in self.rows]
      selected = None
    else:
      key, _, options = self.rows[self.row]
      labels = [tr(label) for label in options]
      selected = self.values.get(key)
      if key == "DrivingSceneView" and selected == -1:
        selected = 0 if device_layout("c4")["scene_style"] else 1
    columns = 2 if self.row is None else len(labels)
    for i, (label, box) in enumerate(zip(labels, grid_cells(rect, len(labels), columns, 12), strict=True)):
      self.targets[i] = box
      rl.draw_rectangle_rounded(box, .14, 5, SELECTED if i in (selected, self._pressed_target) else TILE)
      caption(box, label, 25, MINT if i == selected else INK, centered=True)
      if i == selected:
        rl.draw_rectangle(int(box.x+box.width*.30), int(box.y+box.height*.72), int(box.width*.40), 3, MINT)


class DisplayPage(NavWidget):
  def __init__(self, state):
    super().__init__()
    self.options = self._child(DisplayPicker(state, self.dismiss))
    self.header = self._child(SettingsToolbar(self.options.title, self.options.back))
    for child in (self.options, self.header):
      child.set_enabled(lambda: self.enabled and not self.is_dismissing)

  def show_event(self):
    self.options.row = None
    super().show_event()

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, BASE)
    self.options.render(rl.Rectangle(rect.x+8, rect.y+HEADER_HEIGHT+7, rect.width-16, rect.height-HEADER_HEIGHT-15))
    self.header.render(rl.Rectangle(rect.x, rect.y, rect.width, HEADER_HEIGHT))


class SettingsGrid(DeviceTouchMenu):
  def __init__(self, pages, order):
    super().__init__()
    self.pages, self.order = pages, order
    self.page = 0
    self.page_count = (len(order) + 2) // 3
    self.style = device_layout("c4")

  def title(self):
    return f"{tr('Device settings')}   {self.page+1}/{self.page_count}"

  def can_page(self, direction):
    return 0 <= self.page + direction < self.page_count

  def move(self, direction):
    if self.can_page(direction):
      self.page += direction
      self._pressed_target = None

  def activate(self, key):
    gui_app.push_widget(self.pages[key][1])

  def _render(self, rect):
    self.targets.clear()
    entries = self.order[self.page*3:self.page*3+3]
    for key, box in zip(entries, grid_cells(rect, len(entries), 3, max(12, self.style["menu_spacing"]*.6)), strict=True):
      self.targets[key] = box
      name, _ = self.pages[key]
      rl.draw_rectangle_rounded(box, .14, 6, SELECTED if self._pressed_target == key else TILE)
      path = SECTION_ICONS.get(key)
      if path:
        icon = gui_app.texture("icons_mici/"+path, 47, 47)
        rl.draw_texture_v(icon, rl.Vector2(box.x+(box.width-icon.width)/2, box.y+box.height*.19), MINT)
      y = box.y + (box.height*.49 if path else 0)
      caption(rl.Rectangle(box.x+4, y, box.width-8, box.y+box.height-y), tr(name),
              round(self.style["menu_font"]*.40), centered=True)
