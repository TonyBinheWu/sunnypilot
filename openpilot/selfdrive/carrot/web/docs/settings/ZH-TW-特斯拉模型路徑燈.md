<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_START" param="TeslaModelPathSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉模型路徑燈

**選單:** 駕駛控制 \> 啟動·自動 \> 起步動作

---

<!-- CARROT:SETTING:BEGIN TeslaModelPathSignals -->
<a id="TeslaModelPathSignals"></a>

## 特斯拉模型路徑燈

`TeslaModelPathSignals`

獨立且預設關閉的路徑預測燈：需特斯拉自動轉向燈、資料共享、橫向控制啟用、30km/h 以上、相對車道曲率連續預測越線及新鮮 ONNX 虛線和相鄰車道證據。可能提前或錯誤亮燈；不恢復導航轉彎提前亮燈，不增加掉頭邏輯或轉向許可權。修改後重新啟動，需封閉場地驗證。

<!-- CARROT:AUTO:BEGIN TeslaModelPathSignals -->
<!-- CARROT:AUTO:SOURCE facts="9818c04ff7d27ea918f098a1919b06f295c3974de48008ddd56fadd7ed7e54ce" semantic="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 起步動作
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelPathSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelPathSignals -->
<!-- CARROT:REVIEW reviewed-for="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" reviewed-at="2026-11-08T01:13:19.741652+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

開啟後，根據相對彎曲車道邊界的連續模型路徑越線預測請求燈光；關閉時不使用該預測。需至少四個不同幀持續 0.2 秒、橫向控制啟用、至少 30km/h 及新鮮 ONNX 虛線/相鄰車道證據，不改變模型或轉向命令。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需特斯拉自動轉向燈、資料共享和支援的 CAN/真實撥杆/燈光反饋，修改後重啟。與手動和意圖選項獨立，ATC/App 優先。證據/狀態失效、回退、完成或 12 秒後由原執行器取消；重新觸發前需中立預測和持續熄燈確認。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

可能提前或誤亮，不保證識別每次越線。需兩次不同虛線跨度 0.2 秒、完成年齡最多 0.8 秒，而非拍攝年齡；預設 400ms 間隔不變。虛線不證明顏色、同向或無障礙。不增加導航轉彎預告、轉彎預測或掉頭邏輯；封閉場地實車驗收仍未完成。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelPathSignals -->

<!-- CARROT:SETTING:END TeslaModelPathSignals -->
