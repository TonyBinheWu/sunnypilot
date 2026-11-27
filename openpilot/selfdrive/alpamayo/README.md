# lat2v (Nvidia) 與 Chestnut

Carrot 移植自 Asius 的雙前鏡頭 Alpamayo 2 Edge。模型以道路和廣角影像、車輛運動歷史及可用的導航指令產生推理文字和 6.4 秒軌跡。文字供紀錄使用。控制器使用經時間對齊的軌跡導出曲率與加速度。車機的小模型持續提供感知、車道、里程計及備援動作。

## 選擇與硬體驗證

在停車且車機處於 offroad 時，從原生或網頁模型選擇器的大模型清單選擇 **lat2v (Nvidia)**。車機下載固定版本權重、韌體、編譯圖與獨立的 Python 3.12 執行環境。權重和 GPU 物件會核對 SHA-256。GPU 目標是使用 OS04C10 雙鏡頭的 comma four，搭配 5 Gbps Chestnut 與 gfx1200、8 GiB 顯示記憶體。執行時使用 tinygrad 的 USB AMD 後端和 LLVM 22，預設 100 W、兩個擴散步驟。C3X 的原廠雷達輔助可獨立使用。

驗證在車機本地讀取已完成的雙鏡頭錄影片段，從最新開始搜尋。用相機幀號、曝光開始與結束時間配對 HEVC 索引，再對齊當時的 CAN、里程計與校正。直行、左彎及右彎各須三個連續的有效視窗。每次推理須在 750 ms 內完成，起始速差上限為 2 m/s。比較其後 1.5 秒的實測移動，前向誤差上限為 2 m、橫向為 0.5 m。這是本移植採用的錄檔篩選門檻。缺少場景、GPU 不符或驗證中途點火時，此次選擇不會寫入。成功後才儲存為下次開機選擇。準備記錄和彙總結果位於模型目錄的 lat2v/preparation.log 和 lat2v/replay-result.json。

行駛時監督程式檢查雙鏡頭、小模型與設備健康。modeld 檢查計畫年齡、車速、校正、里程計和曲率限制。接手前需要連續 3 秒可用計畫及未啟用的控制。已啟用控制時若退回小模型，須解除控制且計畫重新穩定才可再切回。車型原有的縱向模式、EPS、Panda、駕駛接管規則仍決定最終輸出。

## 原廠雷達

**低速近距雷達輔助**預設關閉，獨立於模型下載。D 檔、車速大於零且最高 15 km/h 時，已有 radarState 實體雷達關聯的前車在 7 m 內、閉合時間不超過 2 秒、閉合速度大於 0.5 m/s，且同一追蹤 ID 出現三筆不同的新鮮資料時，Carrot 縱向規劃器將正加速度上限降為零。原本較低的減速目標繼續生效。此功能只適用於 openpilot 已啟用直接縱向控制的車型。

側方判定使用同側原廠盲點警示及 radarState 分類的近側雷達目標。沒有目標時，只有支援且啟用的現代／起亞 0x180 或 0x235 角雷達訊息組全部在 200 ms 內更新，才會解除這項側方限制。缺少訊息和舊錄檔都保留為未知。新自動轉彎請求可因此暫緩。lat2v 提出的低速轉彎若側方有目標或資料不足，會退回小模型。模型權重沒有新增雷達輸入，雷達限制位於規劃層。這些量測無法證明巷道兩側牆距、車身掃過空間、前角死角或安全通行寬度。煞停及主動繞障仍需具備相應感測與驗證。

## 驗證範圍與來源

作者在 Asius 裝置記錄的 100 W 道路數值為每秒 3.4 個計畫、推理中位數 115 ms、相機至計畫 258 ms。作者的模型卡也記錄過提前入彎。C4 的效能、熱穩定、閉環轉彎與狹巷障礙物距離需以對應硬體與場地量測。

- [Asius 移植來源，b3690ca](https://github.com/asiusai/openpilot/tree/b3690ca2d9778fba86680f5ef6383a22a7b064aa/openpilot/selfdrive/alpamayo)
- [雙鏡頭 lat2v 權重與模型卡](https://huggingface.co/karelnagel/alpamayo2-edge-lat2v/tree/34c8c070b1557c8df79ebf3688ed0ff840f339a0)
- [NVIDIA Alpamayo 2 Edge 原始碼](https://github.com/NVlabs/alpamayo2-edge/tree/02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e)
- [comma Chestnut 規格](https://comma.ai/shop/chestnut)
- [第三方授權與來源](selected/NOTICE.md)
