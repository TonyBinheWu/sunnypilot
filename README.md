# carrotpilot — 繁體中文

本分支保留在 **[TonyBinheWu/sunnypilot:carrot-wip](https://github.com/TonyBinheWu/sunnypilot/tree/carrot-wip)**，來源為 [ajouatom/openpilot:carrot-wip](https://github.com/ajouatom/openpilot/tree/carrot-wip)，與 `hkg-enhanced` 分開維護。

[繁體中文手機操作指南](docs/CARROT_MOBILE.zh-TW.md) · [上游使用手冊](https://g4iwnl.gitbook.io/carrotpilot) · [上游 Wiki](https://github.com/ajouatom/openpilot/wiki)

![carrotpilot](https://github.com/user-attachments/assets/4d80d256-7e66-4473-a289-04a50733b7e0)

## 繁體中文介面

- **裝置介面**：既有「中文（繁體）」（`zh-CHT`），本次補齊原翻譯檔中未完成的訊息。
- **Carrot Web 手機網頁**：新增獨立「繁體中文」（`zh-tw`），涵蓋選單、對話框、操作狀態、首次使用引導，以及設定名稱、摘要、分類與選項。
- **Android CarrotAssist**：原生介面新增繁中，依手機繁體語系顯示；需重新建置 APK 才會生效，本次未發布或安裝 APK。
- **選擇方式**：手機網頁「工具 → 語言 → 繁體中文」。裝置介面語言需在裝置設定另行選擇，依提示重新啟動。
- **自動偵測**：辨識 `zh-TW`、`zh-Hant`、`zh-HK`、`zh-MO` 與裝置繁中設定；已儲存語言優先，舊使用者請手動切換一次。
- **外部內容**：上游 Wiki 詳細文章及第三方服務依其提供語言顯示。新增繁中介面不代表新增中文語音指令辨識或繁中提示音檔。

## 手機操作

將手機與 comma 連至相同 Wi-Fi／熱點，掃描裝置白色胡蘿蔔圖示的 QR Code，或開啟 `http://裝置IP:7000`。

| 類別 | 可操作內容 |
|---|---|
| 駕駛畫面 | 即時道路影像、HUD、導航、AR、畫面分割、螢幕錄影 |
| 設定 | 搜尋與調整設定、收藏、設定檔、變更歷程、設定說明 |
| 記錄 | 行程影片與資料回放、行程報告、記錄下載／上傳、錄影播放 |
| 工具 | 車型與語言、裝置資訊、Git 更新／切換分支、備份還原、校正與重新啟動 |
| 維護 | 終端機、診斷記錄、遠端支援、eGPU／Jetson 與外部模型狀態 |
| Android CarrotAssist | 尋找裝置、手機直接語音、另行授權的 ChatGPT 設定與駕駛指令 |

完整操作項目與限制見 [手機操作指南](docs/CARROT_MOBILE.zh-TW.md)。網頁、設定及維護操作請先安全停車。語音駕駛指令保留既有權限、車輛條件與駕駛優先權限制。

## 專案與原始說明


carrotpilot 是一個基於 [openpilot](https://github.com/commaai/openpilot) 的獨立駕駛輔助軟體專案，主要面向Hyundai（現代）·Kia（起亞）·Genesis 車輛的相容性、縱向控制品質和真實駕駛體驗進行開發與改進。

carrotpilot 不是由 comma.ai 開發、審查、批准或正式支援的 openpilot 發行版。它包含與上游 openpilot 不同的車輛控制、安全策略和 Driver Monitoring 邏輯，因此不能假設這兩個專案在行為和支援要求上完全相同。

### 安裝與發行策略

在重置裝置後，在安裝地址輸入框中使用以下地址：

```text
i.carrotpilot.app/carrot-wip
```

**上述網址安裝上游版本，不會安裝本倉庫的繁中修改。** 要使用此分支，安裝／更新來源須明確指定 `TonyBinheWu/sunnypilot` 的 `carrot-wip`。本次未建立獨立安裝服務，也未安裝到車機。

`carrot-wip` 是持續開發和釋出同步進行的 rolling branch。為了解決車輛特定問題、風險點和錯誤，程式碼會經常更新，它並不像傳統穩定版那樣長期凍結不變。更新前請確認改動內容，更新後請在能夠立即接管車輛控制的環境中進行驗證。

公開的預構建 `carrot` 分支也存在，但沒有積極維護，因此當前推薦的釋出分支是 `carrot-wip`。


### Jetson 連接與安裝

原始韓文說明記載：2026-09-27 整合後，`carrot-wip` 已包含 Jetson 推論連線、USB 導航影像與儀表、Wi-Fi 資訊傳遞、IP／溫度／錯誤顯示及簽章更新，不需另裝 `carrot-jetlink` 分支。既有 eGPU 的 Cinque v3 與 Jetson 的獨立 Cinque v2 各自保留。

[Windows 安裝指南（韓文）](https://github.com/ajouatom/carrot-jetson/blob/main/docs/INSTALL-WINDOWS-KO.md)說明下載 ZIP、解壓縮並依序執行 **01 → 02** 批次檔，自動準備、修正 USB-C、寫入與驗證映像。

M.2 NVMe SSD 提供相同映像加 **03 共用修補**的實驗路徑，見 [microSD／NVMe 共用修補說明](https://github.com/ajouatom/carrot-jetson/blob/main/docs/jetson_sd_nvme_patch.md)。原始文件註明修補媒體實際開機及 PC 離線修補卡首次實機啟動仍待驗證，見 [整合與驗證範圍](docs/jetson_wip_integration_20260927.md)。

### 支援裝置

- comma three (C3)
- comma 3X (C3X)
- comma four (C4)

部分非原廠或克隆裝置也提供有限相容性，但其硬體配置和品質並不一致。特別是部分裝置沒有可用的駕駛前向攝影機，或者其攝影機支援不正常。這些配置不推薦使用，也不保證裝置相容性或 Driver Monitoring 行為。

“實驗性”或“有限相容”標籤僅用於描述技術成熟度和驗證範圍，並不免除法律要求、安全標準或使用者責任。

### 車輛支援範圍

carrotpilot 的開發和真實反饋主要聚焦Hyundai（現代）·Kia（起亞）·Genesis（HKG）車輛。

倉庫中也包含從 upstream openpilot 繼承來的其他製造商車輛程式碼和支援列表，但這並不意味著這些車輛都已被 carrotpilot 單獨驗證或被積極支援。沒有使用者反饋的製造商和車型無法保證其可用性和品質。

在安裝前，請先查閱 [使用說明書](https://g4iwnl.gitbook.io/carrotpilot) 和 [Wiki](https://github.com/ajouatom/openpilot/wiki)，確認車輛相容性、所需線束和已知限制。

### Hyundai（現代）·Kia（起亞）·Genesis 線束與縱向控制

| 車輛配置 | 常見連線與控制方式 |
|---|---|
| CAN 車輛 | 使用 comma 原廠線束，連線攝影機 |
| CAN-FD 普通車輛 | 使用 comma 原廠線束，連線攝影機 |
| 配備 ADAS 模組的 CAN-FD HDA2 車輛 | 使用單獨線束，連線 ADAS 模組 |

在受支援的 CAN-FD HDA2 配置中，裝置連線到 ADAS 模組，carrotpilot 的 openpilot 縱向控制會直接生成加速和減速指令。這不同於完全依賴原廠 SCC 進行縱向控制的方式。

並非所有車輛和車型年都受支援。即使車名相同，線束、連線位置和縱向控制相容性也可能因平臺、ECU、攝影機和 ADAS 配置而不同，因此請務必確認車輛具體支援資訊。

### 與 upstream openpilot 的差異

#### Vehicle safety 與 CAN 策略

carrotpilot 會在部分安全策略和 CAN 接受條件上與 upstream openpilot 不同。這些調整考慮了受支援車輛上已確認的 CAN 訊息週期、計數器、控制方式以及車輛故障案例。倉庫中包含針對特定訊息或時序條件進行調優的程式碼，旨在避免干擾車輛正常控制流程。

這意味著 carrotpilot 與 comma.ai 官方 safety model 並不完全一致，也不能保證它在所有車輛和場景下都更安全，或滿足特定的功能安全標準。安全相關修改應基於記錄、可重現案例和本倉庫中的測試來評估。

#### Driver Monitoring

carrotpilot 會調整 Driver Monitoring 行為，以減少當駕駛確實在看前方時仍反覆觸發告警的問題。

Driver Monitoring 預設開啟。但在一些無法使用駕駛前向攝影機的硬體上（包括部分非原廠裝置），也提供關閉選項。關閉後，將無法使用基於攝影機的駕駛狀態檢測，以及相關的告警和減速功能，因此不推薦使用此配置。無論 Driver Monitoring 是否啟用，駕駛都應始終注視道路，並準備好隨時接管車輛控制。

### 開發與驗證範圍

本倉庫包含從 openpilot 繼承來的測試，以及 carrotpilot 自有的車輛控制、設定和安全相關測試。但這並不等同於 comma.ai 的官方釋出驗證或內部 HIL（硬體迴路測試）體系，也不意味著所有車輛、線束和裝置組合都已完成驗證。

`carrot-wip` 會根據實際使用回饋持續更新。對於文件中未說明的配置或沒有回饋的車輛，應視為未驗證狀態。

### 法律聲明

在車輛中安裝或修改軟體，可能會受到司法管轄區和車輛配置相關法律、汽車安全要求、檢查規定及保險條款的約束。

以下為原始 README 法律聲明的翻譯：韓國《汽車管理法》限制對可能影響車輛安全行駛的軟體進行任意修改、安裝、增設或刪除。詳細內容請參考 [韓國官方法規資料庫的《汽車管理法》](https://www.law.go.kr/lsInfoP.do?chrClsCd=010102&lsId=001747&lsiSeq=260419&viewCls=lsRvsDocInfoR)。

carrotpilot 是一個正在開發中的駕駛輔助軟體，而不是經認證的車輛零件或自動駕駛產品。本倉庫不對特定場景下的車輛適配性、法律合規性或安全性做出擔保。使用者應自行確認適用法律法規，並對自身裝置、安裝、設定和使用承擔責任。本聲明不構成法律意見。

### 文件

- [CarrotPilot 使用說明書](https://g4iwnl.gitbook.io/carrotpilot)
- [CarrotPilot Wiki](https://github.com/ajouatom/openpilot/wiki)

carrotpilot 的官方公開說明主要以上述使用說明書和 Wiki 為主。請先查閱這些文件，確認車輛要求和設定說明。

### 署名與授權條款

carrotpilot 基於 comma.ai 和 openpilot 貢獻者開發的 [openpilot](https://github.com/commaai/openpilot)。openpilot 以 MIT License 釋出，部分元件可能適用其他授權條款。詳細資訊請檢視 [LICENSE](LICENSE) 和各元件的授權條款聲明。

“openpilot”與 comma 硬體名稱均屬於其相應權利人。carrotpilot 不屬於 comma.ai 的關聯專案，也未獲得 comma.ai 的背書。
