import pyray as rl
from dataclasses import dataclass
from enum import IntEnum
from collections.abc import Callable
from openpilot.selfdrive.ui.layout_profile import large_display_layout
from openpilot.selfdrive.ui.layouts.settings.developer import DeveloperLayout
from openpilot.selfdrive.ui.layouts.settings.device import DeviceLayout
from openpilot.selfdrive.ui.layouts.settings.firehose import FirehoseLayout
from openpilot.selfdrive.ui.layouts.settings.software import SoftwareLayout
from openpilot.selfdrive.ui.layouts.settings.toggles import TogglesLayout
from openpilot.selfdrive.ui.layouts.settings.usbgpu import UsbGpuLayout
from openpilot.selfdrive.ui.device_design import BAR, BASE, INK, MINT, SELECTED, DisplaySettings, TouchMenu, caption, grid_cells, section_label, tile
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.lib.wifi_manager import WifiManager
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NetworkUI

LAYOUT = large_display_layout()


class PanelType(IntEnum):
  DEVICE = 0
  NETWORK = 1
  TOGGLES = 2
  SOFTWARE = 3
  FIREHOSE = 4
  DEVELOPER = 5
  EGPU = 6
  DISPLAY = 7
  CAMERA = 8


@dataclass
class PanelInfo:
  name: str
  instance: Widget


class SettingsLayout(TouchMenu):
  def __init__(self):
    super().__init__()
    self._current_panel = PanelType.DEVICE

    # Panel configuration
    wifi_manager = WifiManager(auto_tethering=True)
    wifi_manager.set_active(False)

    device = DeviceLayout()
    self._more = False
    self._panels = {
      PanelType.DEVICE: PanelInfo(tr_noop("Device info"), device),
      PanelType.NETWORK: PanelInfo(tr_noop("Network"), NetworkUI(wifi_manager)),
      PanelType.TOGGLES: PanelInfo(tr_noop("Toggles"), TogglesLayout()),
      PanelType.SOFTWARE: PanelInfo(tr_noop("Software & power"), SoftwareLayout(device.power_buttons)),
      PanelType.FIREHOSE: PanelInfo(tr_noop("Firehose"), FirehoseLayout()),
      PanelType.DEVELOPER: PanelInfo(tr_noop("Developer"), DeveloperLayout()),
      PanelType.EGPU: PanelInfo(tr_noop("Models & eGPU"), UsbGpuLayout()),
      PanelType.DISPLAY: PanelInfo(tr_noop("Display & units"), DisplaySettings(ui_state)),
      PanelType.CAMERA: PanelInfo(tr_noop("Camera & calibration"), device.camera_panel),
    }

    order = [PanelType[key.upper()] for key in LAYOUT["order"]]
    self._extra = [p for p in order if p in (PanelType.TOGGLES, PanelType.FIREHOSE, PanelType.DEVELOPER)]
    self._primary = [p for p in order if p not in self._extra]
    self._primary.insert(self._primary.index(PanelType.DEVICE) + 1, PanelType.DISPLAY)
    self._primary.insert(self._primary.index(PanelType.SOFTWARE), PanelType.CAMERA)
    self._close_callback: Callable | None = None

  def set_callbacks(self, on_close: Callable):
    self._close_callback = on_close

  def _render(self, rect):
    sidebar = int(rect.width * .26)
    header = min(140, int(rect.height * .14))
    rl.draw_rectangle_rec(rect, BASE)
    rl.draw_rectangle_rec(rl.Rectangle(rect.x, rect.y, sidebar, rect.height), BAR)
    caption(rl.Rectangle(rect.x + 27, rect.y, sidebar - 54, header), tr("Device settings"), 56)
    self.targets.clear()
    panels = self._extra if self._more else self._primary
    nav_area = rl.Rectangle(rect.x + 20, rect.y + header, sidebar - 40, rect.height - header - 22)
    for key, box in zip([*panels, "more"], grid_cells(nav_area, len(panels)+1, 1, LAYOUT["menu_spacing"] / 12), strict=True):
      self.targets[key] = box
      selected = key == self._current_panel
      if selected:
        rl.draw_rectangle_rounded(box, .15, 4, SELECTED)
      text = tr("Back" if self._more else "More settings") if key == "more" else tr(self._panels[key].name)
      section_label(rl.Rectangle(box.x+18, box.y, box.width-36, box.height), key.name.lower() if key != "more" else key,
                    text, int(LAYOUT["menu_font"]*.72), MINT if selected else INK)

    panel = self._panels[self._current_panel]
    left = rect.x + sidebar + 32
    exit_box = rl.Rectangle(rect.x + rect.width - 232, rect.y + 20, 206, header - 40)
    self.targets["close"] = exit_box
    tile(exit_box, tr("Close"), 42)
    caption(rl.Rectangle(left, rect.y, exit_box.x-left-16, header), tr(panel.name), 58)
    panel.instance.render(rl.Rectangle(left, rect.y+header, rect.x+rect.width-left-32, rect.height-header-22))

  def activate(self, key):
    if key == "close":
      if self._close_callback:
        self._close_callback()
    elif key == "more":
      self.set_current_panel(self._primary[0] if self._more else self._extra[0])
    else:
      self.set_current_panel(key)

  def set_current_panel(self, panel_type: PanelType):
    self._more = panel_type in self._extra
    if panel_type != self._current_panel:
      self._panels[self._current_panel].instance.hide_event()
      self._current_panel = panel_type
      self._panels[self._current_panel].instance.show_event()

  def show_event(self):
    super().show_event()
    self._panels[self._current_panel].instance.show_event()

  def hide_event(self):
    super().hide_event()
    self._panels[self._current_panel].instance.hide_event()
