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
    self.enable = Button(self.labels[1], click_callback=lambda: self.select(True), button_style=ButtonStyle.PRIMARY)
    self.disable = Button(self.labels[2], click_callback=lambda: self.select(False), button_style=ButtonStyle.NORMAL)
    self.close = Button(self.labels[3], click_callback=gui_app.pop_widget, button_style=ButtonStyle.NORMAL)

  def select(self, enabled):
    if ui_state.is_offroad():
      choose(enabled)

  def _render(self, rect):
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
