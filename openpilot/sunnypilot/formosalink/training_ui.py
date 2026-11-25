"""Explicit native contribution notice and choice; accessible only while parked."""
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.sunnypilot.formosalink.training_protocol import NOTICE
from openpilot.sunnypilot.formosalink.training_upload import choose, local_state

LABELS = {
  "zh-TW": ("訓練資料授權", "同意並自動上傳", "停止未來上傳", "關閉", "待同步／已停止", "已授權"),
  "en": ("Training data", "Agree and upload", "Stop future uploads", "Close", "Pending / stopped", "Authorized"),
  "ja": ("学習データ提供", "同意して自動送信", "今後の送信を停止", "閉じる", "同期待ち／停止", "同意済み"),
}


def open_training():
  if ui_state.is_offroad():
    gui_app.push_widget(TrainingConsentDialog())


class TrainingConsentDialog(Widget):
  def __init__(self):
    super().__init__()
    from openpilot.sunnypilot.formosalink.ui import language
    self.locale = language()
    self.labels = LABELS[self.locale]
    self.compact = not gui_app.big_ui()
    if self.compact:
      from openpilot.selfdrive.ui.mici.widgets.settings_action import SettingsAction
      from openpilot.system.ui.lib.scroll_panel2 import GuiScrollPanel2
      from openpilot.system.ui.widgets.label import UnifiedLabel
      self._scroll = GuiScrollPanel2(horizontal=False)
      self._scroll.set_enabled(lambda: self.enabled)
      self._notice = UnifiedLabel(NOTICE[self.locale], 20)
    action = SettingsAction if self.compact else Button
    self.enable = action(self.labels[1], click_callback=lambda: self.select(True), button_style=ButtonStyle.PRIMARY)
    self.disable = action(self.labels[2], click_callback=lambda: self.select(False), button_style=ButtonStyle.NORMAL)
    self.close = action(self.labels[3], click_callback=gui_app.pop_widget, button_style=ButtonStyle.NORMAL)
    if self.compact:
      for button in (self.close, self.enable, self.disable):
        button.set_touch_valid_callback(lambda: self.enabled)

  def select(self, enabled):
    if ui_state.is_offroad():
      choose(enabled)

  def _render(self, rect):
    if self.compact:
      return self._render_compact(rect)
    scale = min(rect.width / 536, rect.height / 240)
    margin = 12 * scale
    rl.draw_rectangle_rec(rect, rl.Color(15, 20, 36, 255))
    font = gui_app.font(FontWeight.NORMAL)
    body = NOTICE[self.locale]
    gui_app.fallback_font(body + "".join(self.labels))
    state = local_state()
    title = self.labels[0] + " · " + self.labels[5 if state.get("enabled") and not state.get("pending") else 4]
    rl.draw_text_ex(font, title, rl.Vector2(rect.x + margin, rect.y + margin), 21 * scale, 0, rl.WHITE)
    lines = wrap_text(font, body, 16 * scale, int(rect.width - 2 * margin))
    rl.draw_text_ex(font, "\n".join(lines), rl.Vector2(rect.x + margin, rect.y + 46 * scale), 16 * scale, 0, rl.LIGHTGRAY)
    width = (rect.width - 4 * margin) / 3
    for index, button in enumerate((self.enable, self.disable, self.close)):
      button._label.set_font_size(16 * scale)
      button.render(rl.Rectangle(rect.x + margin + index * (width + margin), rect.y + rect.height - 54 * scale, width, 42 * scale))
    if not ui_state.is_offroad():
      gui_app.pop_widget()
    return -1

  def _render_compact(self, rect):
    from openpilot.selfdrive.ui.device_design import BASE, BAR, INK, caption
    from openpilot.system.ui.lib.multilang import tr
    if not ui_state.is_offroad():
      gui_app.pop_widget()
      return -1
    state = local_state()
    rl.draw_rectangle_rec(rect, BASE)
    rl.draw_rectangle_rec(rl.Rectangle(rect.x, rect.y, rect.width, 58), BAR)
    self.close.set_text(tr("Back"))
    self.close.render(rl.Rectangle(rect.x+6, rect.y+4, 94, 50))
    status = self.labels[5 if state.get("enabled") and not state.get("pending") else 4]
    caption(rl.Rectangle(rect.x+110, rect.y, rect.width-120, 58), self.labels[0]+" · "+status, 21, INK)
    view = rl.Rectangle(rect.x+12, rect.y+62, rect.width-24, rect.height-128)
    height = self._notice.get_content_height(int(view.width))
    offset = self._scroll.update(view, height)
    rl.begin_scissor_mode(int(view.x), int(view.y), int(view.width), int(view.height))
    self._notice.render(rl.Rectangle(view.x, view.y+offset, view.width, max(view.height, height)))
    rl.end_scissor_mode()
    width = (rect.width-28)/2
    for i, button in enumerate((self.enable, self.disable)):
      button.render(rl.Rectangle(rect.x+8+i*(width+12), rect.y+rect.height-58, width, 50))
    return -1
