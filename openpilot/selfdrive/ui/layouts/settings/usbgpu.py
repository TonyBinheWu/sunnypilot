from openpilot.selfdrive.ui.lib.model_choices import ModelChoices
from openpilot.selfdrive.ui.lib.hardware_status import localize_hardware_status
import threading

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.hardware.usbgpu import check_usbgpu, get_usbgpu_device, usbgpu_status
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.list_view import button_item, text_item
from openpilot.system.ui.widgets.scroller_tici import Scroller


class UsbGpuLayout(Widget):
  def __init__(self):
    super().__init__()
    self._checking = False
    self._check_result = "not checked"
    self.choices = ModelChoices(ui_state.is_offroad)
    model_items = [button_item(name, lambda b=big, k=key: self.choices.status(b, k),
                               lambda b=big: tr("External") if b else tr("Internal"),
                               callback=lambda b=big, k=key: self.choices.choose(b, k),
                               enabled=lambda: ui_state.is_offroad() and not self.choices.busy)
                   for big, key, name in self.choices.items]
    for item, (big, key, _) in zip(model_items, self.choices.items, strict=True):
      item.set_visible(lambda b=big, k=key: self.choices.includes(b,k))
    group = button_item(lambda: tr("Model list"), self.choices.group_text, callback=self.choices.next_group)
    search = button_item(lambda: tr("Search models"), lambda: self.choices.query or tr("All models"), callback=self._search)
    empty = text_item(lambda: tr("No matching models"), "")
    empty.set_visible(lambda: not self.choices.visible_models)
    self._scroller = Scroller([group, search, empty, button_item(lambda: tr("Primary driving model after reboot"), self.choices.primary_text,
                  lambda: tr("Choose which selected driving model runs as primary."),
                  callback=self.choices.toggle_primary, enabled=ui_state.is_offroad), *model_items,
      text_item(lambda: tr("eGPU Status"), self._status),
      text_item(lambda: tr("USB Link"), self._link),
      text_item(lambda: tr("Connection Check"), lambda: localize_hardware_status(self._check_result)),
      button_item(lambda: tr("Check eGPU"), lambda: tr("CHECK"),
                  lambda: tr("Checks USB 5 Gbps, firmware, 12V/PCIe, and GPU execution."),
                  callback=self._start_check, enabled=ui_state.is_offroad),
    ], line_separator=True, spacing=0)

  def _search(self):
    from openpilot.system.ui.lib.application import gui_app
    from openpilot.system.ui.widgets import DialogResult
    from openpilot.system.ui.widgets.keyboard import Keyboard
    keyboard = Keyboard(max_text_size=64)
    keyboard.set_title(tr("Search models"))
    keyboard.set_text(self.choices.query)
    keyboard.set_callback(lambda result: self.choices.set_query(keyboard.text) if result == DialogResult.CONFIRM else None)
    gui_app.push_widget(keyboard)

  @staticmethod
  def _status() -> str:
    recovery = getattr(ui_state, 'usbgpu_recovery_badge', None)
    if recovery and not ui_state.usbgpu_active:
      return recovery[0]
    return localize_hardware_status(usbgpu_status(ui_state.usbgpu_compiled, ui_state.usbgpu_loading, ui_state.usbgpu_active,
                         ui_state.usbgpu_startup_failed, compile_pending=ui_state.usbgpu_compile_pending))

  @staticmethod
  def _link() -> str:
    device = get_usbgpu_device()
    if device is None:
      return tr("not connected")
    return f"{device.speed_mbps // 1000} Gbps" if device.speed_mbps >= 1000 and device.speed_mbps % 1000 == 0 \
      else f"{device.speed_mbps} Mbps"

  def _start_check(self):
    if self._checking or not ui_state.is_offroad():
      return
    self._checking = True
    self._check_result = "checking..."

    def run():
      try:
        result = check_usbgpu()
        self._check_result = "no errors" if result is None else result
      finally:
        self._checking = False

    threading.Thread(target=run, name="usbgpu-check", daemon=True).start()

  def show_event(self):
    super().show_event()
    self._scroller.show_event()

  def _render(self, rect):
    self._scroller.render(rect)
