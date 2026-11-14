<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="TESLA_FEATURES" param="TeslaManualLaneSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 特斯拉手動變道燈

**選單:** 駕駛控制 \> Tesla 專用 \> Tesla 功能

---

<!-- CARROT:SETTING:BEGIN TeslaManualLaneSignals -->
<a id="TeslaManualLaneSignals"></a>

## 特斯拉手動變道燈

`TeslaManualLaneSignals`

需開啟特斯拉自動轉向燈和資料共享。30km/h 以上結合駕駛員轉向意圖、持續接近車道線、連續 ONNX 虛線分類與相鄰車道幾何，僅請求左右燈，巡航未啟用也可使用。實線、未知或過期結果禁止新自動請求，不限制真實撥杆。不能證明車道線顏色或同向車流，不增加轉向許可權。預設關閉，修改後重新啟動，需封閉場地實車驗證。

<!-- CARROT:AUTO:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:AUTO:SOURCE facts="1982c03f9b00da4d2d90291548e019b3e9c0e0027d93b3a764aa8ab7fbe51b2d" semantic="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> Tesla 專用 \> Tesla 功能
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaManualLaneSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:REVIEW reviewed-for="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" reviewed-at="2026-11-08T01:13:19.697893+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

開啟後根據持續駕駛員扭矩和兩側邊界接近，僅請求左右燈，巡航未啟用也可使用；關閉時保留既有 ATC/App 燈光。左右均需至少 30km/h、新鮮連續 ONNX 虛線、可信相鄰車道與道路邊界餘量，不寫入轉向 desire。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

需特斯拉自動轉向燈、資料共享、支援的車輛 CAN、真實撥杆及燈光反饋，修改後重啟。視覺盲點開關獨立。人工輸入、雙閃、無效狀態、證據丟失、遠離邊界、越線完成或 12 秒後，透過既有取消/OFF 握手結束。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

至少兩次不同虛線完成時間相隔 0.2 秒，當前年齡不超過 0.8 秒；預設 400ms 推理間隔不變。完成時間不是拍攝時間，虛線不證明白線、同向或無障礙。不恢復導航轉彎預告、不增加距離附加或掉頭實現，不保證輪胎越線前亮燈；仍需封閉場地實車驗收。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaManualLaneSignals -->

<!-- CARROT:SETTING:END TeslaManualLaneSignals -->
