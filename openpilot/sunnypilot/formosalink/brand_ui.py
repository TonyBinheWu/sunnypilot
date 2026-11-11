"""Native companion identity and a visible pairing entry; no driving parameters."""
import pyray as rl

from openpilot.common.basedir import BASEDIR
from openpilot.common.git import get_commit, get_short_branch
from openpilot.sunnypilot.formosalink.ui import language, open_pairing, text
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import multilang
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle

LOGO_ASSET = "../../sunnypilot/formosalink/assets/formosapilot-logo.png"
NATIVE_VERSION = "0.6.2"
COPY = {
  "zh-TW": ("裝置與雲端", "手機配對與遠端設定", "分支", "版本", "行動數據開關：網路設定", "停車後可配對及設定"),
  "en": ("Device & cloud", "Phone pairing & remote settings", "Branch", "Commit", "Cellular data switch: Network", "Park to pair and configure"),
  "ja": ("デバイスとクラウド", "スマートフォン登録・遠隔設定", "ブランチ", "コミット", "モバイル通信：ネットワーク設定", "登録と設定は停車中のみ"),
}


class FormosaPilotPanel(Widget):
  def __init__(self, embedded=False):
    super().__init__()
    self.embedded = embedded
    self.branch = get_short_branch(BASEDIR) or "unknown"
    self.commit = (get_commit(BASEDIR) or "unknown")[:7]
    self.logo = gui_app.texture(LOGO_ASSET, 180, 180)
    self._pair = Button(lambda: "FormosaLink · " + text("scan"), open_pairing,
                        font_size=36 if gui_app.big_ui() else 16, text_padding=6, button_style=ButtonStyle.PRIMARY)
    from openpilot.selfdrive.ui.ui_state import ui_state
    self._pair.set_enabled(ui_state.is_offroad)
    self._close = Button(lambda: text("close"), gui_app.pop_widget,
                         font_size=34 if gui_app.big_ui() else 15, text_padding=6)

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, rl.Color(13, 23, 30, 255))
    # Proportional to the panel, not the full screen: C3X reserves a sidebar.
    scale = min(rect.width / 536, rect.height / 240)
    x, y = rect.x + 16*scale, rect.y + 12*scale
    font = gui_app.font(FontWeight.NORMAL)
    labels = COPY[language()]
    # Load the complete page's glyphs before issuing draw commands. Growing a
    # fallback atlas halfway through a frame can invalidate earlier draw batches.
    if multilang.requires_font_fallback():
      gui_app.fallback_font("\n".join(labels) + text("scan") + text("close") + "FormosaLink ·")

    def line(value, top, size=16, color=rl.WHITE):
      rl.draw_text_ex(font, value, rl.Vector2(x, rect.y + top*scale), size*scale, 0, color)

    logo_rect = rl.Rectangle(x, y, 54*scale, 54*scale)
    rl.draw_texture_pro(self.logo, rl.Rectangle(0, 0, self.logo.width, self.logo.height), logo_rect, rl.Vector2(0, 0), 0, rl.WHITE)
    rl.draw_text_ex(font, "FormosaPilot " + NATIVE_VERSION, rl.Vector2(x+64*scale, y+5*scale), 23*scale, 0, rl.WHITE)
    rl.draw_text_ex(font, labels[0], rl.Vector2(x+64*scale, y+34*scale), 15*scale, 0, rl.Color(87, 209, 188, 255))
    line(labels[1], 77)
    line(f"{labels[2]}: {self.branch} · {labels[3]}: {self.commit}", 104, 14)
    line("formosapilot.dinglu-t.com", 128, 14)
    line(labels[4], 151, 14)
    line(labels[5], 174, 12, rl.Color(160, 180, 185, 255))
    width = rect.width - 32*scale
    if not self.embedded:
      width -= 90*scale
      self._close.render(rl.Rectangle(rect.x+rect.width-96*scale, rect.y+199*scale, 80*scale, 32*scale))
    self._pair.render(rl.Rectangle(x, rect.y+199*scale, width, 32*scale))
