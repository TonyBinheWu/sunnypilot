import pyray as rl

from openpilot.selfdrive.ui.device_design import BASE
from openpilot.selfdrive.ui.layout_profile import device_layout
from openpilot.selfdrive.ui.mici.layouts.settings.navigation import HEADER_HEIGHT, SettingsToolbar, add_section_navigation
from openpilot.system.ui.lib.multilang import tr_noop
from openpilot.selfdrive.ui.mici.layouts.settings.menu import DisplayPage, SettingsGrid
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


class SettingsLayout(NavWidget):
  def __init__(self):
    super().__init__()
    from openpilot.sunnypilot.formosalink.ui import mici_pair_button
    device = DeviceLayoutMici()
    links = NavScroller()
    links._scroller.add_widgets([PairBigButton(), mici_pair_button()])
    pages = {
      "device": (tr_noop("Device info"), device),
      "display": (tr_noop("Display & units"), DisplayPage(ui_state)),
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
    for title, page in pages.values():
      if isinstance(page, NavScroller):
        add_section_navigation(page, title)
    self.menu = self._child(SettingsGrid(pages, ["display", "network", "egpu", "device", "camera", "software", *extra]))
    self.header = self._child(SettingsToolbar(self.menu.title, self.dismiss, lambda: self.menu.move(-1),
                                              lambda: self.menu.move(1), self.menu.can_page))
    for child in (self.menu, self.header):
      child.set_enabled(lambda: self.enabled and not self.is_dismissing)

  def show_event(self):
    self.menu.page = 0
    super().show_event()

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, BASE)
    self.menu.render(rl.Rectangle(rect.x+8, rect.y+HEADER_HEIGHT+8, rect.width-16, rect.height-HEADER_HEIGHT-16))
    self.header.render(rl.Rectangle(rect.x, rect.y, rect.width, HEADER_HEIGHT))
