<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DEVICE" param="CommaPedalEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Comma Pedal縱向控制

**選單:** 車輛與硬體 \> 裝置硬體

---

<!-- CARROT:SETTING:BEGIN CommaPedalEnabled -->
<a id="CommaPedalEnabled"></a>

## Comma Pedal縱向控制

`CommaPedalEnabled`

允許在未配備ACC的車輛上透過Comma Pedal裝置進行縱向控制。僅適用於CC\_ONLY\_CAR車輛，且車輛的Cruise ready必須關閉。Cruise ready開啟時原廠巡航優先，無法使用Comma Pedal控制。

<!-- CARROT:AUTO:BEGIN CommaPedalEnabled -->
<!-- CARROT:AUTO:SOURCE facts="b43cabcca251d1f420557f397d427a1dfa9657bc8fc6303a173917584a19df6b" semantic="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 車輛與硬體 \> 裝置硬體
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CommaPedalEnabled -->

<!-- CARROT:MANUAL:BEGIN CommaPedalEnabled -->
<!-- CARROT:REVIEW reviewed-for="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" reviewed-at="2026-11-03T12:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 動作

僅在具有明確踏板配置的 CC_ONLY_CAR 車輛上，檢測到裝置且滿足安全條件時允許踏板控制。當前配置適用於 Kia Ray EV。原廠 Cruise ready 或巡航啟用、輸入無效、制動或駕駛員踩下加速踏板時阻止踏板輸出。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

設定位於車輛與硬體 → 裝置硬體。確認車輛和踏板配置後修改設定並重啟，以應用車輛引數及 Panda 韌體更新。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

CarrotPilot 實車執行、制動和停車保持仍需單獨驗證。貢獻者報告的加速受限問題尚未解決。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CommaPedalEnabled -->

<!-- CARROT:SETTING:END CommaPedalEnabled -->
