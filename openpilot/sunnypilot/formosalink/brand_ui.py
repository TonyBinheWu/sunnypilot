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
NATIVE_VERSION = "0.8.0"
COPY = {
  "zh-TW": ("裝置與雲端", "手機配對與遠端設定", "分支", "版本", "行動數據開關：網路設定", "停車後可配對及設定"),
  "en": ("Device & cloud", "Phone pairing & remote settings", "Branch", "Commit", "Cellular data switch: Network", "Park to pair and configure"),
  "ja": ("デバイスとクラウド", "スマートフォン登録・遠隔設定", "ブランチ", "コミット", "モバイル通信：ネットワーク設定", "登録と設定は停車中のみ"),
}


from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.system.ui.widgets.scroller_tici import Scroller


class FormosaPilotPanel(NavScroller if not gui_app.big_ui() else Widget):
  def __init__(self, embedded=False):
    super().__init__()
    self.embedded = embedded
    self.branch = get_short_branch(BASEDIR) or "unknown"
    self.commit = (get_commit(BASEDIR) or "unknown")[:7]
    self.logo = gui_app.texture(LOGO_ASSET, 80, 80)
    if gui_app.big_ui():
      from openpilot.system.ui.widgets.list_view import text_item
      from openpilot.system.ui.sunnypilot.widgets.list_view import button_item_sp
      self._pair = button_item_sp("FormosaLink", lambda:text("scan"), callback=open_pairing)
      self._scroller = Scroller([
        text_item("FormosaPilot", NATIVE_VERSION),
        text_item(lambda:COPY[language()][2], self.branch),
        text_item(lambda:COPY[language()][3], self.commit),
        self._pair,
      ], line_separator=True)
    else:
      from openpilot.selfdrive.ui.mici.widgets.button import BigButton
      class BrandButton(BigButton):
        def _get_label_font_size(self):
          return 36
      self._pair = BrandButton("FormosaLink", text("scan"), self.logo)
      self._pair.set_click_callback(open_pairing)
      self._branch_card = BigButton(COPY[language()][2], self.branch, scroll=True)
      self._commit_card = BigButton(COPY[language()][3], self.commit)
      self._scroller.add_widgets([
        BrandButton("FormosaPilot", NATIVE_VERSION, self.logo),
        self._branch_card,
        self._commit_card,
        self._pair,
      ])
    from openpilot.selfdrive.ui.ui_state import ui_state
    self._pair.set_enabled(ui_state.is_offroad)

  def _update_state(self):
    super()._update_state()
    if not gui_app.big_ui():
      self._branch_card.set_text(COPY[language()][2])
      self._commit_card.set_text(COPY[language()][3])
      self._pair.set_value(text("scan"))

  def _render(self, rect):
    if gui_app.big_ui():
      self._scroller.render(rect)
    else:
      super()._render(rect)
