"""Local-only persistent SIM data preference, independent of Wi-Fi/RF power."""
from ipaddress import IPv4Address, AddressValueError

TEXT = {
  "zh-TW": {
    "title":"SIM 行動數據",
    "description":"停車時可切換，關閉後停止 SIM 行動數據連線，Wi-Fi 仍可使用。SIM 卡不需拔除，也不刪除 eSIM。沒有 Wi-Fi 時網頁會離線，請在裝置重新開啟。",
    "on":"開啟", "off":"關閉",
  },
  "en": {
    "title":"SIM mobile data",
    "description":"Change while parked. Turning this off stops SIM data while keeping Wi-Fi available. No SIM removal or eSIM deletion. Without Wi-Fi the web dashboard goes offline; turn data back on at the device.",
    "on":"On", "off":"Off",
  },
  "ja": {
    "title":"SIM モバイルデータ",
    "description":"停車中に切り替えます。オフにすると SIM データ通信を停止し、Wi-Fi は使用できます。SIM の取り外しや eSIM の削除は不要です。Wi-Fi がなければウェブはオフラインになるため、本体で再びオンにしてください。",
    "on":"オン", "off":"オフ",
  },
}

for language, values in {
  "zh-TW": ("行動數據已關閉", "正在停止行動數據", "尚未連線・正在撥號", "數據連線已建立", "尚未連線・搜尋網路", "網路拒絕註冊", "未連線", "數據機狀態無法確認"),
  "en": ("Mobile data off", "Stopping mobile data", "Not connected · dialing", "Data link connected", "Not connected · searching", "Network registration denied", "Not connected", "Modem status unavailable"),
  "ja": ("モバイル通信オフ", "モバイル通信を停止中", "未接続・接続試行中", "データ接続済み", "未接続・網を検索中", "網への登録が拒否されました", "未接続", "モデム状態を確認できません"),
}.items():
  TEXT[language].update(zip(("disabled", "stopping", "starting", "connected", "searching", "denied", "disconnected", "unknown"), values))


def connection_status(enabled, modem, now):
  """Fresh data bearer status, not SIM registration or an Internet reachability claim."""
  stamp = modem.get("seconds_since_boot")
  if type(stamp) not in (int, float) or not 0 <= now-stamp <= 10:
    return "unknown"
  state = modem.get("state")
  if not enabled:
    return "disabled" if state == "DATA_DISABLED" and modem.get("connected") is False else "stopping"
  try:
    ip = IPv4Address(modem.get("ip_address", ""))
    if modem.get("connected") is True and not ip.is_unspecified:
      return "connected"
  except (AddressValueError, TypeError):
    pass
  if modem.get("registration") == "denied":
    return "denied"
  if state == "SEARCHING":
    return "searching"
  if state in ("INITIALIZING", "CONNECTING", "CONNECTED", "DATA_DISABLED"):
    return "starting"
  return "disconnected"


def label(key, language=None):
  if language is None:
    from openpilot.system.ui.lib.multilang import multilang
    language = multilang.language
  language = "zh-TW" if language in ("zh-CHT", "zh-TW", "zh-Hant") else "ja" if language == "ja" else "en"
  return TEXT[language][key]


def modem_data_state(enabled, modem, now):
  stamp = modem.get("seconds_since_boot")
  if type(stamp) not in (int,float) or not 0 <= now-stamp <= 10:
    return "unknown"
  if modem.get("state") == "DATA_DISABLED":
    return "disabled"
  if modem.get("connected") is True:
    return "connected"
  return "disconnected" if enabled else "pending"


class CellularDataPreference:
  def __init__(self, params, offroad):
    self.params, self.offroad = params, offroad

  @property
  def enabled(self):
    return self.params.get("GsmDataEnabled", return_default=True) is not False

  def set_enabled(self, enabled):
    if type(enabled) is not bool or not self.offroad():
      return False
    self.params.put_bool("GsmDataEnabled", enabled, block=True)
    return True
