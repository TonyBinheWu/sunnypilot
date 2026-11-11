<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviDecelCancelEarlyWarning" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速中止：提前警告修正 \[實驗\]

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<a id="VehicleNaviDecelCancelEarlyWarning"></a>

## 減速中止：提前警告修正 \[實驗\]

`VehicleNaviDecelCancelEarlyWarning`

實驗功能，僅在減速中止請求開啟時有效。原車導航測速警告通常在攝影機前約 6.1m×限速（60km/h 約 366m）開始，但在部分地區或車輛上會更早開始（60km/h 約 460m），導致箱式、固定、移動區間預告無法匹配而被視為未識別型別。開啟後將匹配視窗的遠端最多擴大至 1.35 倍，使這類警告也能識別型別。⚠ 風險：視窗擴大後，附近的移動攝影機（移動測速區間）預告可能被錯誤匹配到其他警告。此時若開啟了“減速中止：移動測速區間”或導航減速模式（AutoNaviSpeedCtrlMode）為 2 及以下（忽略移動區間），則有較低機率跳過實際測速攝影機的減速。開啟後務必在實際駕駛中確認其行為。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:AUTO:SOURCE facts="ed5b08c2ce225fb53a83cb9d9b147cb2eb28915a419053cbfe62b7e2f09cbd94" semantic="ca6595f1bd5ba33a43b5c946ad4d3a7cb99440c06da4c111043f7d1654d3b7c6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelEarlyWarning -->
