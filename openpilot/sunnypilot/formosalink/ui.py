"""Offroad-only FormosaLink QR pairing, shared by C3X and C4 layouts."""
import queue
import threading
import time

import pyray as rl

from openpilot.common.qrcode import make_texture
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.formosalink.identity import default_directory
from openpilot.sunnypilot.formosalink.pairing import request_pairing, pairing_status
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import multilang
from openpilot.system.ui.lib.wrap_text import wrap_text
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle

TEXT = {
  "zh-TW": {"scan":"掃描 QR 配對", "intro":"用手機相機掃描 QR Code，透過 GitHub 登入並確認。僅啟用唯讀狀態回報，不提供遠端行車控制。", "start":"產生配對 QR", "disable":"停用監看", "close":"關閉", "loading":"正在安全連線…", "pending":"請用手機掃描，再確認配對。", "paired":"已配對・唯讀監看已啟用", "error":"無法連線。請檢查網路與時間後重試。", "expired":"QR 已過期，請重新產生。", "revoked":"配對已撤銷，請在本機明確建立新身分。", "offroad":"請停車後再操作。", "disabled":"唯讀監看已停用。"},
  "en": {"scan":"Scan QR to pair", "intro":"Scan with your phone camera, sign in with GitHub and confirm. Only read-only status reporting is enabled. No remote driving controls.", "start":"Show pairing QR", "disable":"Disable monitoring", "close":"Close", "loading":"Connecting securely…", "pending":"Scan with your phone, then confirm pairing.", "paired":"Paired · read-only monitoring enabled", "error":"Cannot connect. Check network and device clock, then retry.", "expired":"QR expired. Generate a new one.", "revoked":"Pairing revoked. Explicitly create a new local identity to reconnect.", "offroad":"Park before pairing.", "disabled":"Read-only monitoring disabled."},
  "ja": {"scan":"QR で登録", "intro":"スマートフォンで QR を読み取り、GitHub でログインして確認します。状態の読み取り専用送信のみ有効にします。遠隔運転操作はありません。", "start":"登録用 QR を表示", "disable":"監視を停止", "close":"閉じる", "loading":"安全に接続中…", "pending":"スマートフォンで読み取り、登録を確認してください。", "paired":"登録済み・読み取り専用監視が有効", "error":"接続できません。ネットワークと時刻を確認してください。", "expired":"QR の期限切れです。再発行してください。", "revoked":"登録解除済みです。本体で新しい ID を明示的に作成してください。", "offroad":"停車してから操作してください。", "disabled":"読み取り専用監視を停止しました。"},
}
TEXT["zh-TW"]["compact_intro"] = "手機掃描 QR，登入 GitHub 後確認。\n僅開啟唯讀監看。"
TEXT["en"]["compact_intro"] = "Scan with your phone.\nSign in with GitHub and confirm.\nRead-only monitoring."
TEXT["ja"]["compact_intro"] = "スマートフォンで QR を読み取り、\nGitHub でログインして確認。\n読み取り専用の監視です。"

for locale, on, off in (("zh-TW", "停車遠端設定：開", "停車遠端設定：關"), ("en", "Parked settings: on", "Parked settings: off"), ("ja", "停車中の遠隔設定：オン", "停車中の遠隔設定：オフ")):
  TEXT[locale].update(remote_on=on, remote_off=off)
TEXT["zh-TW"].update(intro="掃描 QR 配對。可在此允許停車時從網頁修改設定。", compact_intro="掃描 QR 配對。\n遠端設定限停車時使用。", paired="已配對", disabled="監看已停用。")
TEXT["en"].update(intro="Scan to pair. Enable parked settings below to edit from the web.", compact_intro="Scan to pair.\nRemote settings while parked.", paired="Paired", disabled="Monitoring disabled.")
TEXT["ja"].update(intro="QR を読み取って登録します。停車中の遠隔設定を下で許可できます。", compact_intro="QR で登録。\n遠隔設定は停車中のみ。", paired="登録済み", disabled="監視を停止しました。")


def language():
  code = multilang.language
  return "zh-TW" if code in ("zh-CHT", "zh-TW", "zh-Hant") else "ja" if code == "ja" else "en"


def text(key):
  return TEXT[language()][key]


def open_pairing():
  if ui_state.is_offroad():
    gui_app.push_widget(FormosaPairingDialog())


def formosalink_button():
  from openpilot.system.ui.sunnypilot.widgets.list_view import button_item_sp
  return button_item_sp("FormosaLink", lambda: text("scan"), callback=open_pairing, enabled=ui_state.is_offroad)


def add_mici_pair_button(scroller):
  from openpilot.selfdrive.ui.mici.widgets.button import BigButton
  class PairButton(BigButton):
    def _get_label_font_size(self):
      return 56

    def _update_state(self):
      self.set_value(text("scan"))
  button = PairButton("FormosaLink", text("scan"), gui_app.texture("icons_mici/settings/device/pair.png", 33, 60))
  button.set_click_callback(open_pairing)
  button.set_enabled(ui_state.is_offroad)
  scroller.add_widget(button)


class FormosaPairingDialog(Widget):
  def __init__(self, directory=None):
    super().__init__()
    self.directory = directory or default_directory()
    self._events = queue.SimpleQueue()
    self._generation = 0
    self._active = True
    self._busy = False
    self._next_poll = 0.0
    self._expires = 0.0
    self._state = "intro"
    self._qr_texture = None
    big = gui_app.big_ui()
    padding = 20 if big else 8
    self._close = Button(lambda: text("close"), self._close_dialog, font_size=40 if big else 14, text_padding=padding, button_style=ButtonStyle.NORMAL)
    self._start = Button(lambda: text("start"), self._request, font_size=40 if big else 14, text_padding=padding, button_style=ButtonStyle.PRIMARY)
    self._disable = Button(lambda: text("disable"), self._disable_monitoring, font_size=36 if big else 12, text_padding=padding)
    self._start.set_enabled(lambda: not self._busy and ui_state.is_offroad())
    self._disable.set_enabled(ui_state.is_offroad)
    self._remote = Button(lambda: text("remote_on" if ui_state.params.get_bool("FormosaLinkRemoteSettings") else "remote_off"), self._toggle_remote,
                          font_size=34 if big else 11, text_padding=padding)
    self._remote.set_enabled(ui_state.is_offroad)

  def _toggle_remote(self):
    if ui_state.is_offroad():
      ui_state.params.put_bool("FormosaLinkRemoteSettings", not ui_state.params.get_bool("FormosaLinkRemoteSettings"), block=True)

  def _clear_qr(self):
    if self._qr_texture is not None:
      rl.unload_texture(self._qr_texture)
      self._qr_texture = None

  def _close_dialog(self):
    gui_app.pop_widget()

  def hide_event(self):
    super().hide_event()
    self._active = False
    self._generation += 1
    self._clear_qr()

  def _worker(self, kind):
    if self._busy or not self._active or not ui_state.is_offroad():
      return
    self._busy = True
    generation = self._generation
    def work():
      try:
        result = request_pairing(self.directory) if kind == "enroll" else pairing_status(self.directory)
      except Exception:
        # Do not log identity material, signed frames or QR credentials.
        result = {"error": True}
      self._events.put((generation, kind, result))
    threading.Thread(target=work, name="formosalink-pair", daemon=True).start()

  def _request(self):
    if ui_state.is_offroad() and not self._busy:
      self._clear_qr()
      self._state = "loading"
      self._worker("enroll")

  def _disable_monitoring(self):
    if not ui_state.is_offroad():
      return
    self._generation += 1
    self._busy = False
    self._clear_qr()
    self._state = "disabled"
    self._expires = 0
    ui_state.params.put_bool("FormosaLinkEnabled", False)
    ui_state.params.put_bool("FormosaLinkRemoteSettings", False, block=True)

  def _update_state(self):
    if not ui_state.is_offroad():
      if self._state != "offroad":
        self._generation += 1
      self._busy = False
      self._clear_qr()
      self._state = "offroad"
      self._expires = 0
      return
    while not self._events.empty():
      generation, kind, result = self._events.get()
      if generation != self._generation or not self._active:
        continue
      self._busy = False
      self._next_poll = time.monotonic()+5
      if result.get("error"):
        self._state = "error"
        self._next_poll += 5
      elif result["state"] == "paired":
        self._clear_qr()
        self._expires = 0
        self._state = "paired"
        ui_state.params.put_bool("FormosaLinkEnabled", True)
      elif result["state"] == "revoked":
        self._clear_qr()
        self._expires = 0
        self._state = "revoked"
        ui_state.params.put_bool("FormosaLinkEnabled", False)
      elif kind == "enroll":
        self._clear_qr()
        self._qr_texture = make_texture(result["url"])
        rl.set_texture_filter(self._qr_texture, rl.TextureFilter.TEXTURE_FILTER_POINT)
        self._expires = result["expires_at"]
        self._state = "pending"
        # Explicit local opt-in; the agent cannot send telemetry until the server
        # confirms ownership. It can continue after this QR screen is closed.
        ui_state.params.put_bool("FormosaLinkEnabled", True)
      else:
        self._state = "pending"
    if self._expires and time.time() >= self._expires:
      self._clear_qr()
      self._expires = 0
      self._state = "expired"
    if self._expires and time.monotonic() >= self._next_poll:
      self._worker("status")

  def _render(self, rect):
    rl.draw_rectangle_rec(rect, rl.Color(15, 20, 36, 255))
    scale = min(rect.width/2160, rect.height/1080)
    margin = 60*scale
    close_width, button_height = 290*scale, 120*scale
    self._close.render(rl.Rectangle(rect.x+rect.width-close_width-margin, rect.y+margin, close_width, button_height))
    font = gui_app.font(FontWeight.BOLD)
    body_font = gui_app.font(FontWeight.NORMAL)
    rl.draw_text_ex(font, "FormosaLink", rl.Vector2(rect.x+margin,rect.y+margin+25*scale), 75*scale, 0, rl.WHITE)
    width = int(rect.width*.53-margin)
    y = rect.y+margin+180*scale
    body_size = 44 if gui_app.big_ui() else 60
    line_height = 52 if gui_app.big_ui() else 70
    lines = wrap_text(body_font, text("intro" if gui_app.big_ui() else "compact_intro"), body_size*scale, width)
    rl.draw_text_ex(body_font, "\n".join(lines), rl.Vector2(rect.x+margin,y), body_size*scale, 0, rl.Color(165, 177, 202, 255))
    y += len(lines)*line_height*scale+50*scale
    if self._state != "intro":
      state_lines = wrap_text(body_font, text(self._state), 42*scale, width)
      rl.draw_text_ex(body_font, "\n".join(state_lines), rl.Vector2(rect.x+margin,y), 42*scale, 0, rl.Color(172, 151, 255, 255))
    bottom = rect.y+rect.height-margin-button_height
    self._remote.render(rl.Rectangle(rect.x+margin,bottom-button_height-20*scale,1000*scale,button_height))
    self._start.render(rl.Rectangle(rect.x+margin,bottom,660*scale,button_height))
    self._disable.render(rl.Rectangle(rect.x+margin+690*scale,bottom,420*scale,button_height))
    if self._qr_texture is not None:
      available = min(rect.width*.4,rect.height-2*margin-button_height-50*scale)
      # Integral module scaling keeps the QR sharp on the 536x240 C4 profile.
      modules = self._qr_texture.width//10  # common.qrcode renders each module at 10 px
      qr_size = max(modules, int(available/modules)*modules)
      target = rl.Rectangle(rect.x+rect.width-margin-qr_size,rect.y+margin+button_height+25*scale,qr_size,qr_size)
      self._last_qr_rect = target
      rl.draw_texture_pro(self._qr_texture,rl.Rectangle(0,0,self._qr_texture.width,self._qr_texture.height),target,rl.Vector2(0,0),0,rl.WHITE)
    return -1
