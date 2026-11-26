import datetime
import time

import pyray as rl
from collections.abc import Callable
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.widgets.device_home import DeviceHome
from openpilot.system.ui.lib.application import gui_app, MousePos
from openpilot.selfdrive.ui.ui_state import ui_state

class MiciHomeLayout(Widget):
  def __init__(self):
    super().__init__()
    self._on_settings_click: Callable | None = None
    self._on_carrot_web_click: Callable | None = None

    self._last_refresh = 0
    self._mouse_down_t: None | float = None
    self._did_long_press = False
    self._is_pressed_prev = False

    self._version_text = None
    self._experimental_mode = False

    self._ip_address = "Offline"

    self.home = DeviceHome(True)

  def show_event(self):
    super().show_event()
    self._version_text = self._get_version_text()
    self._ip_address = self._read_network_address(ui_state.params_memory)
    self._update_params()

  def _update_params(self):
    self._experimental_mode = ui_state.params.get_bool("ExperimentalMode")

  @staticmethod
  def _read_network_address(params_memory) -> str:
    address = (params_memory.get("NetworkAddress") or "").strip()
    return address if address and address != "0.0.0.0" else "Offline"

  def _update_state(self):
    if self.is_pressed and not self._is_pressed_prev:
      self._mouse_down_t = time.monotonic()
    elif not self.is_pressed and self._is_pressed_prev:
      self._mouse_down_t = None
      self._did_long_press = False
    self._is_pressed_prev = self.is_pressed

    if self._mouse_down_t is not None:
      if self.home.pressed == "mode" and self.home.hit(gui_app.last_mouse_event.pos) == "mode" and time.monotonic() - self._mouse_down_t > 0.5:
        # long gating for experimental mode - only allow toggle if longitudinal control is available
        if ui_state.has_longitudinal_control:
          self._experimental_mode = not self._experimental_mode
          ui_state.params.put("ExperimentalMode", self._experimental_mode)
        self._mouse_down_t = None
        self._did_long_press = True

    if rl.get_time() - self._last_refresh > 5.0:
      # Update version text
      self._version_text = self._get_version_text()
      self._ip_address = self._read_network_address(ui_state.params_memory)
      self._last_refresh = rl.get_time()
      self._update_params()

  def set_callbacks(self, on_settings: Callable | None = None, on_carrot_web: Callable | None = None):
    self._on_settings_click = on_settings
    self._on_carrot_web_click = on_carrot_web

  def _handle_mouse_press(self, mouse_pos: MousePos):
    self.home.pressed = self.home.hit(mouse_pos)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    target = self.home.hit(mouse_pos)
    if target and target == self.home.pressed and not self._did_long_press:
      if target == "settings" and self._on_settings_click:
        self._on_settings_click()
      elif target == "web" and self._on_carrot_web_click:
        self._on_carrot_web_click()
      elif target == "remote" and gui_app.remote_screen:
        gui_app.remote_screen.arm()
    self.home.pressed = None
    self._did_long_press = False

  def _get_version_text(self) -> tuple[str, str, str, str] | None:
    version = ui_state.params.get("Version")
    branch = ui_state.params.get("GitBranch")
    commit = ui_state.params.get("GitCommit")

    if not all((version, branch, commit)):
      return None

    commit_date_raw = ui_state.params.get("GitCommitDate")
    try:
      unix_ts = int(commit_date_raw.strip("'").split()[0])
      date_str = datetime.datetime.fromtimestamp(unix_ts).strftime("%Y/%m/%d")
    except (ValueError, IndexError, TypeError, AttributeError):
      date_str = ""

    return version, branch, commit[:7], date_str

  def _render(self, rect):
    branch = " · ".join(self._version_text[1:3]) if self._version_text else "—"
    self.home.render(rect, branch, self._ip_address, self._experimental_mode)
