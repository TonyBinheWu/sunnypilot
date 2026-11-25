import pyray as rl
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.selfdrive.ui.layout_profile import device_layout
from openpilot.selfdrive.ui.device_design import BASE, INK, TILE, DisplaySettings, TouchMenu, caption, grid_cells, section_label, tile
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.selfdrive.ui.mici.layouts.settings.language import LanguageLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.toggles import TogglesLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.network.network_layout import NetworkLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici, PairBigButton
from openpilot.selfdrive.ui.mici.layouts.settings.developer import DeveloperLayoutMici
from openpilot.selfdrive.ui.mici.layouts.settings.firehose import FirehoseLayout
from openpilot.selfdrive.ui.mici.layouts.settings.usbgpu import UsbGpuLayoutMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app


class DisplayPage(NavWidget):
  def __init__(self):
    super().__init__()
    self.options = self._child(DisplaySettings(ui_state))
    self.options.set_enabled(lambda: self.enabled and not self.is_dismissing)
    self.back_box = rl.Rectangle(0, 0, 0, 0)
    self.back_pressed = False

  def _handle_mouse_press(self, pos):
    self.back_pressed = rl.check_collision_point_rec(pos, self.back_box)

  def _handle_mouse_release(self, pos):
    if self.back_pressed and not self.is_dismissing and rl.check_collision_point_rec(pos, self.back_box):
      self.dismiss()
    self.back_pressed = False

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, BASE)
    self.back_box = rl.Rectangle(rect.x+8, rect.y+8, 65, 42)
    tile(self.back_box, tr("Back"), 17)
    caption(rl.Rectangle(rect.x+83, rect.y+8, rect.width-95, 42), tr("Display & units"), 23)
    self.options.render(rl.Rectangle(rect.x+8, rect.y+55, rect.width-16, rect.height-61))


class SettingsGrid(TouchMenu):
  def __init__(self, pages, primary, extra, close):
    super().__init__()
    self.pages, self.primary, self.extra = pages, primary, extra
    self.close = close
    self.more = False
    self.style = device_layout("c4")

  def activate(self, key):
    if key == "back":
      if self.more:
        self.more = False
      else:
        self.close()
    elif key == "more":
      self.more = True
    else:
      gui_app.push_widget(self.pages[key][1])

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, BASE)
    self.targets.clear()
    self.targets["back"] = rl.Rectangle(rect.x+8, rect.y+8, 65, 42)
    tile(self.targets["back"], tr("Back"), 17)
    caption(rl.Rectangle(rect.x+83, rect.y+8, rect.width-205, 42), tr("More settings" if self.more else "Device settings"), 23)
    if not self.more:
      self.targets["more"] = rl.Rectangle(rect.x+rect.width-119, rect.y+8, 111, 42)
      tile(self.targets["more"], tr("More settings"), 16)
    entries = self.extra if self.more else self.primary
    area = rl.Rectangle(rect.x+8, rect.y+56, rect.width-16, rect.height-64)
    for key, box in zip(entries, grid_cells(area, len(entries), gap=self.style["menu_spacing"]*.3), strict=True):
      self.targets[key] = box
      rl.draw_rectangle_rounded(box, .16, 4, TILE)
      section_label(rl.Rectangle(box.x+8, box.y, box.width-16, box.height), key, tr(self.pages[key][0]),
                    round(self.style["menu_font"]*.32), INK)


class SettingsLayout(NavWidget):
  def __init__(self):
    super().__init__()
    from openpilot.sunnypilot.formosalink.ui import mici_pair_button
    device = DeviceLayoutMici()
    links = NavScroller()
    links._scroller.add_widgets([PairBigButton(), mici_pair_button()])
    pages = {
      "device": (tr_noop("Device info"), device),
      "display": (tr_noop("Display & units"), DisplayPage()),
      "network": (tr_noop("Network"), NetworkLayoutMici()),
      "egpu": (tr_noop("Models & eGPU"), UsbGpuLayoutMici()),
      "camera": (tr_noop("Camera & calibration"), device.camera_panel),
      "software": (tr_noop("Software & power"), device.software_panel),
      "toggles": (tr_noop("toggles"), TogglesLayoutMici()),
      "language": (tr_noop("Language"), LanguageLayoutMici()),
      "developer": (tr_noop("developer"), DeveloperLayoutMici()),
      "firehose": (tr_noop("firehose"), FirehoseLayout()),
      "pair": (tr_noop("Pair Device"), links),
    }
    extra = [key for key in device_layout("c4")["order"] if key in ("toggles", "language", "developer", "firehose", "pair")]
    self.menu = self._child(SettingsGrid(pages, ("device", "display", "network", "egpu", "camera", "software"), extra, self.dismiss))
    self.menu.set_enabled(lambda: self.enabled and not self.is_dismissing)

  def _render(self, rect):
    self.menu.render(rect)
