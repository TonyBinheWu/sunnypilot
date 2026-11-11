<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_START" param="TeslaAutoTurnSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉自動轉向燈

**選單:** 駕駛控制 \> 啟動·自動 \> 起步動作

---

<!-- CARROT:SETTING:BEGIN TeslaAutoTurnSignals -->
<a id="TeslaAutoTurnSignals"></a>

## 特斯拉自動轉向燈

`TeslaAutoTurnSignals`

僅適用於車輛 CAN 與真實撥杆有效的 Model 3/Y。不再導航提前打轉彎燈，用實測航向和回正判定完成；僅已確認點亮的轉彎可在新鮮許可權下停車等待，保留變道準備亮燈。駕駛員優先，不增加轉向或起步許可權。預設關閉，修改後需重新啟動。未經封閉場地實車驗證，不應用於公共道路。

<!-- CARROT:AUTO:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:AUTO:SOURCE facts="42decc10e44675ce20850a2a2e7cf23b3e88d6a80b2c4973d14756817cde7490" semantic="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 起步動作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoTurnSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:REVIEW reviewed-for="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" reviewed-at="2026-11-08T01:13:19.645605+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

轉彎燈從既有轉彎 desire 開始，不因導航準備或距離提前點亮；變道保留準備亮燈確認。完成需新鮮實測航向變化 20°、目標方向轉向超過 30°，再以至少 1 km/h 移動且回正至 ±15°。僅已確認 TX/點亮的轉彎可在新鮮橫向許可權和健康姿態下停車等待，不適用於新請求或變道。後續候選等待當前完成及有效轉彎 desire，最多排隊三秒，同方向保持 ID。60 秒上限、新 idle 模板與逐次 TX 回報、駕駛員優先和取消/OFF 確認均保留。反饋丟失則退出，取消未確認則本次執行禁止自動輸出。PC 測試不能證明實車持續點亮。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

預設關閉，修改後需重啟。要求受支援的 Model 3/Y、與自動巡航滾輪共用的 CAN1 拓展線檢測（`0x3DF`）、有效且新鮮的真實撥杆輸入及匹配的 Panda 韌體。收到 CAN1 撥杆後優先使用該來源；輸入陳舊或衝突時禁止自動輸出。仍需獨立的燈控模板及 UI/物理燈反饋；App 請求保持至既有動作完成。`blocked:*`、`waiting:*` 用於記錄具體阻斷原因，不是新增螢幕告警。不增加轉向或起步許可權。公共道路使用前必須在目標車輛的封閉場地驗證左右燈、故障和人工接管；CAN 斷線或裝置斷電時無法保證物理熄燈。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

執行：`openpilot/selfdrive/car/tesla_turn_signals.py`。意圖：`openpilot/selfdrive/controls/lib/desire_helper.py`。安全層：`opendbc_repo/opendbc/safety/safety/safety_tesla_turn_signals.h`。診斷與限制見 Tesla 使用者指南。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaAutoTurnSignals -->

<!-- CARROT:SETTING:END TeslaAutoTurnSignals -->
