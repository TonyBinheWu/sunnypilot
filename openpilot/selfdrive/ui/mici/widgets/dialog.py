import abc
import pyray as rl
from typing import Union
from collections.abc import Callable
from openpilot.system.ui.widgets.nav_widget import NavWidget
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.widgets.mici_keyboard import MiciKeyboard
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.lib.application import font_fallback, gui_app, FontWeight, MousePos, TextAlignment
from openpilot.system.ui.widgets.slider import BigSlider
from openpilot.system.ui.lib.scroll_panel2 import GuiScrollPanel2
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.device_design import BASE, BAR, INK, MINT, SELECTED, TILE, caption
from openpilot.selfdrive.ui.mici.layouts.settings.navigation import DeviceTouchMenu, SettingsDetail
from openpilot.selfdrive.ui.mici.widgets.button import BigCircleButton, BigButton


class BigDialogBase(NavWidget, abc.ABC):
  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))


class BigDialog(SettingsDetail, BigDialogBase):
  def __init__(self, title: str, description: str, icon: Union[rl.Texture, None] = None):
    super().__init__()
    self.init_settings_header(title or "Device settings")
    self._message = UnifiedLabel(description, 26, font_weight=FontWeight.MEDIUM, text_color=INK)
    self._scroll = GuiScrollPanel2(horizontal=False)
    self._scroll.set_enabled(lambda: self.enabled and not self.is_dismissing)
    self._icon = icon

  def _render_body(self, rect):
    box = rl.Rectangle(rect.x+8, rect.y+7, rect.width-16, rect.height-15)
    rl.draw_rectangle_rounded(box, .14, 5, TILE)
    x = box.x + 14
    if self._icon:
      rl.draw_texture_v(self._icon, rl.Vector2(x, box.y+12), MINT)
      x += self._icon.width + 12
    view = rl.Rectangle(x, box.y+8, box.x+box.width-x-14, box.height-16)
    height = max(view.height, self._message.get_content_height(int(view.width)))
    offset = self._scroll.update(view, height)
    rl.begin_scissor_mode(int(view.x), int(view.y), int(view.width), int(view.height))
    self._message.render(rl.Rectangle(view.x, view.y+offset, view.width, height))
    rl.end_scissor_mode()


class ConfirmationSlider(BigSlider):
  def __init__(self, title, icon, callback, red):
    super().__init__(title, icon, confirm_callback=callback)
    self.red = red
    self._label.set_font_size(32)
    self._label.set_text_color(INK)
    self._label.set_alignment(TextAlignment.LEFT)
    self._label.set_shimmer(False)

  def _render(self, rect):
    track = rl.Rectangle(rect.x+8, rect.y+8, rect.width-16, rect.height-16)
    rl.draw_rectangle_rounded(track, .14, 5, TILE)
    self._label.render(rl.Rectangle(track.x+20, track.y+22, track.width-216, track.height-34))
    # Keep the original slider travel, start region and release threshold.
    handle = rl.Rectangle(track.x+track.width-180+self._scroll_x_circle_filter.x, track.y, 180, track.height)
    rl.draw_rectangle_rounded(handle, .14, 5, rl.Color(110, 52, 48, 255) if self.red else SELECTED)
    mid = int(handle.y+handle.height/2)
    rl.draw_triangle(rl.Vector2(handle.x+8, mid), rl.Vector2(handle.x+22, mid+11), rl.Vector2(handle.x+22, mid-11), INK)
    rl.draw_texture_v(self._icon, rl.Vector2(handle.x+(handle.width-self._icon.width)/2+6,
                                             handle.y+(handle.height-self._icon.height)/2), INK)


class BigConfirmationDialog(SettingsDetail, BigDialogBase):
  def __init__(self, title: str, icon: rl.Texture, confirm_callback: Callable[[], None],
               exit_on_confirm: bool = True, red: bool = False):
    super().__init__()
    self.init_settings_header("Confirm action")
    self._confirm_callback = confirm_callback
    self._exit_on_confirm = exit_on_confirm
    self._slider = self._child(ConfirmationSlider(title, icon, self._on_confirm, red))
    self._slider.set_enabled(lambda: self.enabled and not self.is_dismissing)
    self.header.set_enabled(lambda: self.enabled and not self.is_dismissing and not self._slider.confirmed)

  def _on_confirm(self):
    if self._exit_on_confirm:
      self.dismiss(self._confirm_callback)
    elif self._confirm_callback:
      self._confirm_callback()

  def _update_state(self):
    super()._update_state()
    if self.is_dismissing and not self._slider.confirmed:
      self._slider.reset()

  def _render_body(self, rect):
    self._slider.render(rect)


class InputActions(DeviceTouchMenu):
  def __init__(self, dialog):
    super().__init__()
    self.dialog = dialog
    self.repeat_at = None
    self.repeated = False

  def _handle_mouse_press(self, pos):
    super()._handle_mouse_press(pos)
    self.repeated = False
    self.repeat_at = rl.get_time()+.5 if self._pressed_target == "erase" else None

  def activate(self, key):
    if key == "back":
      self.dialog.dismiss()
    elif key == "confirm":
      self.dialog.submit()
    elif not self.repeated:
      self.dialog._keyboard.backspace()

  def _render(self, rect):
    keyboard = self.dialog._keyboard
    text = keyboard.text()
    if self.enabled and self._pressed_target == "erase" and self.repeat_at is not None and rl.get_time() >= self.repeat_at:
      keyboard.backspace()
      self.repeated = True
      self.repeat_at = rl.get_time()+.08
    rl.draw_rectangle_rec(rect, BAR)
    self.targets.clear()
    for key, label, x, width, enabled in (
      ("back", tr("Back"), rect.x+6, 88, True),
      ("erase", tr("Delete"), rect.x+rect.width-172, 76, bool(text)),
      ("confirm", tr("OK"), rect.x+rect.width-90, 84, len(text) >= self.dialog._minimum_length),
    ):
      box = rl.Rectangle(x, rect.y+4, width, rect.height-8)
      if enabled:
        self.targets[key] = box
      rl.draw_rectangle_rounded(box, .2, 5, SELECTED if self._pressed_target == key else TILE)
      caption(box, label, 21, INK if enabled else rl.GRAY, centered=True)

    field = rl.Rectangle(rect.x+102, rect.y+5, rect.width-282, rect.height-10)
    value = text + keyboard.get_candidate_character()
    if not value:
      caption(field, self.dialog.hint, 21)
      return
    font = font_fallback(gui_app.font(FontWeight.MEDIUM), value)
    width = measure_text_cached(font, value, 25).x
    rl.begin_scissor_mode(int(field.x), int(field.y), int(field.width), int(field.height))
    rl.draw_text_ex(font, value, rl.Vector2(field.x+min(0, field.width-width), field.y+(field.height-25)/2), 25, 0, INK)
    rl.end_scissor_mode()


class BigInputDialog(BigDialogBase):
  BACK_TOUCH_AREA_PERCENTAGE = 0.2

  def __init__(self, hint: str, default_text: str = "", minimum_length: int = 1,
               confirm_callback: Callable[[str], None] | None = None, auto_return_to_letters: str = ""):
    super().__init__()
    self.hint = hint
    self._minimum_length = minimum_length
    self._confirm_callback = confirm_callback
    self._keyboard = self._child(MiciKeyboard(auto_return_to_letters=auto_return_to_letters))
    self._keyboard.set_text(default_text)
    self.actions = self._child(InputActions(self))
    for child in (self._keyboard, self.actions):
      child.set_enabled(lambda: self.enabled and not self.is_dismissing)

  def submit(self):
    text = self._keyboard.text()
    if not self.is_dismissing and len(text) >= self._minimum_length:
      self.dismiss((lambda: self._confirm_callback(text)) if self._confirm_callback else None)

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, BASE)
    self._keyboard.render(rect)
    self.actions.render(rl.Rectangle(rect.x, rect.y, rect.width, rect.height-self._keyboard.get_keyboard_height()))


class BigDialogButton(BigButton):
  def __init__(self, text: str, value: str = "", icon: Union[str, rl.Texture] = "", description: str = ""):
    super().__init__(text, value, icon)
    self._description = description

  def _handle_mouse_release(self, mouse_pos: MousePos):
    super()._handle_mouse_release(mouse_pos)

    dlg = BigDialog(self.text, self._description)
    gui_app.push_widget(dlg)


class BigConfirmationCircleButton(BigCircleButton):
  def __init__(self, title: str, icon: rl.Texture, confirm_callback: Callable[[], None], exit_on_confirm: bool = True,
               red: bool = False, icon_offset: tuple[int, int] = (0, 0)):
    super().__init__(icon, red, icon_offset)
    self.settings_title = title

    def show_confirm_dialog():
      gui_app.push_widget(BigConfirmationDialog(title, icon, confirm_callback,
                                                exit_on_confirm=exit_on_confirm, red=red))

    self.set_click_callback(show_confirm_dialog)
