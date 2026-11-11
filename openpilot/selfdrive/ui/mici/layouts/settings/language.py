from openpilot.common.params import Params
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigDialog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import multilang, tr
from openpilot.system.ui.widgets.scroller import NavScroller


class LanguageLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._params = Params()
    self._buttons = {}
    for name, code in multilang.languages.items():
      button = BigButton(name)
      # Language names must be readable before that language has been selected.
      button._label.set_font_weight(FontWeight.UNIFONT)
      button.set_enabled(ui_state.is_offroad)
      button.set_click_callback(lambda code=code: self._select(code))
      self._buttons[code] = button
      self._scroller.add_widget(button)

  def show_event(self):
    super().show_event()
    current = (self._params.get("LanguageSetting") or "en").removeprefix("main_")
    for code, button in self._buttons.items():
      button.set_value(tr("Selected") if code == current else "")

  def _select(self, code):
    if not ui_state.is_offroad() or code not in self._buttons:
      return
    self._params.put("LanguageSetting", code)
    self.show_event()
    gui_app.push_widget(BigDialog(tr("Language saved"), tr("Restart your device from Device settings to apply the language.")))
