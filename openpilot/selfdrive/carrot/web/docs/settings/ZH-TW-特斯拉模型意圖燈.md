<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="TESLA_FEATURES" param="TeslaModelDesireSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉模型意圖燈

**選單:** 駕駛控制 \> Tesla 專用 \> Tesla 功能

---

<!-- CARROT:SETTING:BEGIN TeslaModelDesireSignals -->
<a id="TeslaModelDesireSignals"></a>

## 特斯拉模型意圖燈

`TeslaModelDesireSignals`

獨立且預設關閉的變道預測燈：需特斯拉自動轉向燈、資料共享、橫向控制啟用、30km/h 以上、連續模型變道機率及新鮮 ONNX 虛線和相鄰車道證據。可能提前或錯誤亮燈，不使用導航轉彎預告，不實現掉頭，也不增加轉向許可權。修改後重新啟動，需封閉場地驗證。

<!-- CARROT:AUTO:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:AUTO:SOURCE facts="f4c6ef89da8178e4203f15e604fb296d0aa2cb9dc3c28d684bbf55cd2561eaf9" semantic="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> Tesla 專用 \> Tesla 功能
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelDesireSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:REVIEW reviewed-for="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" reviewed-at="2026-11-08T01:13:19.722451+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

開啟後，優勢變道機率在至少四個不同模型幀中持續 0.2 秒時請求燈光；關閉時不使用該預測。需橫向控制啟用、至少 30km/h 及手動燈相同的新鮮 ONNX 虛線/相鄰車道證據，不生成轉向請求。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需特斯拉自動轉向燈、資料共享和支援的 CAN/真實撥杆/燈光反饋，修改後重啟。與手動及路徑選項獨立，既有 ATC/App 意圖優先。證據丟失、完成、回退或 12 秒時取消；連續預測不能在中立預測和持續熄燈確認前重放已消費的觀察。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

可能提前或誤亮。需兩次不同虛線結果跨度 0.2 秒、完成年齡不超過 0.8 秒，而非總拍攝年齡；預設 400ms 推理不變。不證明顏色、同向或無障礙，不增加導航轉彎預告、轉彎預測或掉頭實現。PC 測試不等於實車驗收。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelDesireSignals -->

<!-- CARROT:SETTING:END TeslaModelDesireSignals -->
