# 道路物件辨識：網頁與 APK

更新 carrot-wip 車機並重新啟動，重新開啟網頁／APK。在「工具／診斷 → 網頁設定」開啟 **三角錐與斑馬線辨識（實驗性）**，進入 Carrot Vision、選用座艙視覺或 BEV，再連線觀看道路鏡頭。原版 CarrotAssist 與獨立 Carrot Cockpit 都載入這套車機網頁；這部分不需要新增 Android 權限或安裝另一個模型 App。

| 項目 | 實際支援狀態 |
| --- | --- |
| 三角錐 | 已接入 YOLOv8 Safety Cone 權重。顯示繁中影像提示；新鮮 ROAD 相機校正與高度有效時另顯示近似 3D 錐體 |
| 斑馬線 | 已接入原作者 YOLOv5s6 權重並轉換固定320px ONNX。顯示繁中影像辨識提示；偵測框不能代表實際地面輪廓，因此不畫虛構條紋或距離 |
| 停止線 | **未完成辨識**：目前找不到適用前向車載鏡頭、權重公開且散布授權明確的可部署模型 |
| 機車停等區 | **未完成辨識**：同上。機車停等區不同於路口的機車兩段式左轉待轉區 |

## 設定與效能

預設關閉，與原有「前方影像物件辨識」分開。一般人車／動物模型繼續使用原有流程；道路模型失敗不會停掉它。網頁與 APK 的觀看裝置執行 CPU WASM，不占用車機駕駛模型的推論執行緒，不上傳影像。

首次載入的 runtime 與權重約74MB。需要 Worker、WebAssembly SIMD、OffscreenCanvas、createImageBitmap，建議更新 Android System WebView。使用一個道路工作程序、一次一張影格，每秒最多4次並依推論耗時降頻。目標1.2秒未更新即清除；慢到結果過期時顯示繁中提示，不把舊目標留在畫面。載入失敗／4秒推論逾時會停止，可關閉重開重試；離開 Vision、切換來源、進入背景或凍結標註會清除／終止。寬鏡頭、裁切畫面、未知相機或缺少校正時不產生三角錐的地面位置，但仍可顯示影像辨識提示。

這兩個模型沒有經過臺灣道路、夜雨、遠距小物件或實體 Android 盒子完整驗收。桌面應用程式內瀏覽器的測試約0.58–0.65秒／張（兩模型合計），不是 Android 效能承諾；原作者斑馬線影片三個影格及一張 CC0 三角錐照片有辨識結果，空白圖無結果。轉換前後輸出通過比對，這些結果不能換算準確率。未分類雷達目標保持未知；顯示不會改變轉向、煞車、跟車、紅綠燈停車或控制模型。

## 模型與授權

[完整來源、對應原始碼、權重雜湊與授權](../../openpilot/selfdrive/carrot/web/vendor/road-detector/NOTICE.md)。斑馬線模型為 GPL-3.0；三角錐模型卡為 CC-BY-4.0，但 ONNX 內嵌 AGPL-3.0，兩種聲明均保留，並附原始權重與匹配的 Ultralytics 原始碼。這些資產不宣稱是 Tesla 的模型。原有功能與其他元件的授權不變。

重現斑馬線匯出：在隔離環境依 `requirements-export.txt` 安裝版本，CPU Torch 可從其官方 CPU 索引取得，執行 `python tools/carrot_road_models/export_crosswalk.py --output crosswalk.onnx`。它核對附帶來源雜湊，用受限 `weights_only=True` 載入、匯出 opset12，檢查 ONNX 與 PyTorch／原生 ORT 空白輸出；不使用 unrestricted pickle。

## 補齊停止線與機車停等區所需條件

[RLMD](https://github.com/stu9113611/RLMD) 的25類定義確實包含 crosswalk（2）、stop line（3）、motor waiting zone（20）、left turn box（21）。[RMSeg-UDA](https://github.com/stu9113611/RMSeg-UDA) 提供相關訓練程式；截至2026-11-17查核，作者公開庫未提供可直接使用的預訓練 checkpoint 或明確的模型／資料散布許可。因此本次沒有下載資料訓練或把未知授權權重塞進 APK。

要接入，需取得作者預訓練權重及可散布許可（包含資料使用權），或另備授權清楚的臺灣前鏡頭標註影像進行訓練。模型需清楚區分停止線、斑馬線、機車停等區與待轉區，並以獨立測試集評估每類 precision／recall、夜雨、遮擋、距離及不同裝置延遲，再接入分割輪廓與相機標定。空拍待轉區模型、白線幾何規則與斑馬線矩形不能代替這兩個辨識類別。
