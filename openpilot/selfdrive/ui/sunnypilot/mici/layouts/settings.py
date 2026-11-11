"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.sunnypilot.formosalink.brand_ui import FormosaPilotPanel, LOGO_ASSET
from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.layouts.settings.settings import SettingsBigButton
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici, PairBigButton
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.selfdrive.ui.mici.widgets.button import BigCircleButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog, BigDialog
from openpilot.sunnypilot.formosalink.ui import open_pairing
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import multilang, tr
from openpilot.system.ui.widgets.scroller import NavScroller

ICON_SIZE = 70
BIG_ICON_SIZE = 110


class FormosaBigButton(SettingsBigButton):
  def _get_label_font_size(self):
    return 36


class SunnylinkBigButton(SettingsBigButton):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._label.set_font_weight(FontWeight.AUDIOWIDE)

  def _get_label_font_size(self):
    # Audiowide runs wider than Inter: "sunnylink" wraps to two lines at 64
    return 56


class LanguageLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._buttons = {}
    for name, code in multilang.languages.items():
      button = BigButton(name)
      button._label.set_font_weight(FontWeight.UNIFONT)
      button.set_click_callback(lambda selected=code: self._select_language(selected))
      self._scroller.add_widget(button)
      self._buttons[code] = button
    self._refresh()

  def _select_language(self, code: str):
    if not ui_state.is_offroad():
      return
    multilang.change_language(code)
    self._refresh()

  def _refresh(self):
    for code, button in self._buttons.items():
      button.set_value(tr("Selected") if code == multilang.language else "")


class DeviceLayoutSP(DeviceLayoutMici):
  def __init__(self):
    super().__init__()
    self._scroller._items[:] = [item for item in self._scroller._items if not isinstance(item, PairBigButton)]
    self._language_button = BigButton("language", multilang.codes.get(multilang.language, "English"),
                                      gui_app.texture("icons_mici/settings/device/info.png", 64, 64))
    self._language_button.set_click_callback(lambda: gui_app.push_widget(LanguageLayoutMici()))
    self._language_button.set_enabled(ui_state.is_offroad)
    self._scroller.add_widget(self._language_button)
    from openpilot.sunnypilot.formosalink.ui import add_mici_pair_button
    add_mici_pair_button(self._scroller)

  def _update_state(self):
    super()._update_state()
    self._language_button.set_value(multilang.codes.get(multilang.language, "English"))


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    device_panel = DeviceLayoutSP()
    self._scroller._items[2].set_click_callback(lambda: gui_app.push_widget(device_panel))

    self.icon_offroad_enable = gui_app.texture("../../sunnypilot/selfdrive/assets/icons_mici/always_offroad.png", BIG_ICON_SIZE,
                                               BIG_ICON_SIZE)
    self.icon_offroad_disable = gui_app.texture("../../sunnypilot/selfdrive/assets/icons_mici/disable_offroad.png", BIG_ICON_SIZE,
                                                BIG_ICON_SIZE)
    self.icon_offroad_slider = gui_app.texture("icons_mici/settings/device/lkas.png", BIG_ICON_SIZE, BIG_ICON_SIZE)

    formosalink_btn = FormosaBigButton("FormosaLink", "", gui_app.texture(LOGO_ASSET, 80, 80))
    formosalink_btn.set_click_callback(open_pairing)

    models_panel = ModelsLayoutMici()
    models_btn = SettingsBigButton("models", "", gui_app.texture("../../sunnypilot/selfdrive/assets/offroad/icon_models.png", ICON_SIZE, ICON_SIZE))
    models_btn.set_click_callback(lambda: gui_app.push_widget(models_panel))

    # onroad: enable button sits at the front (left of toggles)
    self._enable_offroad_btn_onroad = BigCircleButton(self.icon_offroad_enable, red=True)
    self._enable_offroad_btn_onroad.set_click_callback(lambda: self._handle_always_offroad(True))
    self._enable_offroad_btn_onroad.set_visible(lambda: ui_state.started and not ui_state.always_offroad)

    # offroad: enable button sits at the end (right of developer)
    self._enable_offroad_btn_offroad = BigCircleButton(self.icon_offroad_enable, red=True)
    self._enable_offroad_btn_offroad.set_click_callback(lambda: self._handle_always_offroad(True))
    self._enable_offroad_btn_offroad.set_visible(lambda: not ui_state.started and not ui_state.always_offroad)

    self._disable_offroad_btn = BigCircleButton(self.icon_offroad_disable, red=False)
    self._disable_offroad_btn.set_click_callback(lambda: self._handle_always_offroad(False))
    self._disable_offroad_btn.set_visible(lambda: ui_state.always_offroad)

    formosa_panel = FormosaPilotPanel()
    formosa_btn = FormosaBigButton("FormosaPilot", "FormosaLink", gui_app.texture(LOGO_ASSET, 80, 80))
    formosa_btn.set_click_callback(lambda: gui_app.push_widget(formosa_panel))

    items = self._scroller._items.copy()

    items.insert(1, models_btn)
    items.insert(5, formosalink_btn)

    items.insert(0, formosa_btn)

    # front slots (only one ever visible at a time): exit-always-offroad, then enable-onroad
    items.insert(0, self._enable_offroad_btn_onroad)
    items.insert(0, self._disable_offroad_btn)
    # end slot: enable-offroad (right of developer)
    items.append(self._enable_offroad_btn_offroad)

    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)

  def _update_state(self):
    super()._update_state()

  def _handle_always_offroad(self, enable: bool):

    def _set_offroad_status(status: bool):
      if not ui_state.engaged:
        ui_state.params.put_bool("OffroadMode", status)
        ui_state.always_offroad = status

    if not enable:
      dlg = BigConfirmationDialog(tr("slide to exit always offroad"), self.icon_offroad_slider, red=False,
                                  confirm_callback=lambda: _set_offroad_status(False))
    else:
      if ui_state.engaged:
        gui_app.push_widget(BigDialog(tr("disengage to enable always offroad"), "", ))
        return

      dlg = BigConfirmationDialog(tr("slide to force offroad"), self.icon_offroad_slider, red=True,
                                  confirm_callback=lambda: _set_offroad_status(True))
    gui_app.push_widget(dlg)
