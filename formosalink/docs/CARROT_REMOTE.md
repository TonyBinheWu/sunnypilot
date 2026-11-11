# CarrotPilot 雲端網頁與雙鏡頭 LIVE

本分支 `carrot-wip` 接入既有 FormosaLink。入口為 [FormosaLink](https://formosapilot.dinglu-t.com)，以原有 GitHub 帳號與獨立裝置 QR 配對使用。已存在於 `/data/formosalink` 的身分可沿用；車機與 IIS 都須更新。

## 車機設定

1. 更新本倉庫 `carrot-wip`，安全停車後重新啟動。
2. C3X 在「裝置 → FormosaLink」開啟配對；C4 在「設定 → FormosaLink」開啟。
3. 掃描 QR，於手機登入 GitHub，核對並完成配對。
4. 要使用原生 Carrot 網頁時，在車機配對畫面開啟「遠端 Carrot 網頁」。此權限預設關閉，與原有 FormosaLink 停車設定權限分開。
5. 車機須保持網路連線。遠端網頁需要停車熄火、有效的裝置狀態與 Panda 狀態；資料過期時會關閉通道。

本機參數 `FormosaLinkEnabled` 預設開啟背景連線，但仍需配對；`FormosaLinkRemoteWeb` 預設關閉，控制原生 Carrot 網頁通道。Carrot 的 FormosaLink 健康面板只提供讀取，設定操作使用原生 Carrot 網頁；沒有套用 sunnypilot 的車型設定 schema。原有 `FormosaLinkRemoteSettings` 不會自動授予完整網頁權限。

## 遠端操作 Carrot 網頁

登入 FormosaLink，在 `carrot-wip` 裝置卡片選「遠端 Carrot 網頁」，於新分頁開啟原生介面。可使用既有的繁中設定搜尋、參數調整、說明、備份與工具；原生 Carrot 自己的驗證、生效時機與確認流程仍會執行。完整網頁也包含原有終端與維護能力，因此這是完整網頁授權。

每個分頁固定綁定一台裝置。兩台裝置同時開啟時，HTTP、WebSocket、靜態資源與瀏覽器偏好各自路由；沒有共用的「目前裝置」cookie。FormosaLink cookie 不會轉送給車機；Carrot 自己的 Bearer 授權可沿通道傳遞。

通訊路徑為手機 HTTPS/WSS → IIS → FormosaLink relay → 車機主動建立的已簽署 WSS → 固定 `127.0.0.1:7000`。不需公開車機 7000 埠。伺服器每次請求及串流傳送都重查登入與裝置所有權，裝置則檢查本機授權與停車狀態。撤銷授權、登出、解除配對或開始行車會關閉通道；已送達原生工具的操作仍依該工具的執行結果處理。

HTTP 上傳的整個請求內容上限為 8 MiB。下載支援串流與 Range，傳輸採分段確認及回壓；每台裝置最多 16 個同時處理的請求／WebSocket。離線不會自動重送操作。Carrot 原生 WebRTC 的 ICE／NAT 限制仍存在；HTTP/WebSocket 通道不會轉送 UDP。遠端鏡頭請使用下面的 FormosaLink LIVE。

## 前廣角／車內鏡頭 LIVE

在裝置卡片選「雙鏡頭 LIVE」，或進入裝置工作區的「即時影像」。選擇「前廣角」或「車內」後開始觀看，可停止、全螢幕，並依瀏覽器能力使用子母畫面或本機錄影。兩個分頁可分別觀看不同鏡頭。

既有串流為連續 WebSocket MJPEG，目標 8 fps、最大 640×360、保留長寬比，不含音訊；沒有宣稱固定延遲或 30 fps。每路使用持續、單執行緒、低優先序的 FFmpeg，讀取既有 VisionIPC，不修改相機共享影格。Carrot 車內鏡頭使用其 `VISION_STREAM_DRIVER`，並兼容沒有 `uv_offset` 的 NV12 影格。

觀看需要登入所有者，短效租約最長 15 秒。關閉／背景化網頁或停止觀看後，租約到期便停止編碼；無人觀看時不持續上傳。最新影格與解碼確認限制排隊，資料過期會清除畫面。伺服器不自動保存影像；手動錄影只保存在目前瀏覽器。完整機制見 [LIVE_STREAMING.md](LIVE_STREAMING.md)。

## IIS 更新

### 按鈕重載或一直等待影像

- 若點車機「遠端 Carrot 網頁」後 UI 重載，請更新至修正 Carrot Params 寫入介面的版本並重新啟動。此按鈕只切換本機網頁授權，不應重新啟動 UI 或整台裝置。
- 在 FormosaLink 按「開始觀看」便會自動建立短效觀看租約、喚醒鏡頭並傳送；不需另外執行手動影像發送指令。等待期間請確認車機在線，亦可切換前廣角／車內鏡頭交叉檢查。
- 鏡頭時間戳使用包含休眠時間的 Linux 開機時鐘；接收端也必須使用相同時鐘。新版修正休眠後新影像被誤判無效的情況，仍會拒絕過期或未來影像。
- 更新車機並重新啟動後，關閉舊網頁再重新開啟。網站模組版本為 `0.8.1`；若仍看到「需先在來源端明確啟動發送」，表示仍載入舊頁面，請重新整理或清除該站快取。
- 若仍無影像，需檢查車機 `formosalink` 與 `camerad` 程序的實際錯誤。背景鏡頭初始化失敗會重試，串流錯誤以鏡頭名稱及錯誤類別記錄，每路最多每 30 秒一則，不記錄身分金鑰或影像內容。單靠等待提示無法判斷鏡頭、編碼器及網路哪一段失敗。

部署工具只更新 manifest 管理的程式與網站檔案；執行階段帳號、OAuth、配對與資料庫位於站台外。新版私有 Python 套件也包含遠端網頁所需的 bridge 資源。

在 **192.168.20.145 IIS 主機**以系統管理員 PowerShell 執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython
```

更新程式沿用既有設定，不需要重新提供 GitHub Secret。完成後 `/api/v1/health` 必須同時出現 `carrot-web-v1` 與 `live-camera-stream-v1`。只更新 IIS 靜態檔案不會重啟已載入舊 Python 程式的後端。IIS 仍需 ARR、URL Rewrite、WebSocket 與既有有效 HTTPS 憑證。

## 驗證範圍

測試使用真實本機 TCP、Uvicorn、原生通道客戶端與模擬的本機 Carrot HTTP/WebSocket 服務，涵蓋設定寫入與回讀、1 MiB 分段下載、二進位／繁中 WebSocket、CSRF、跨所有者拒絕、防重播、本機授權撤銷與連線清理。既有雙鏡頭串流測試與新的 Carrot DRIVER/NV12 適配測試一併執行。

這些是主機與協定測試。C3X／C4 實體鏡頭、夜間車內影像、CPU／溫度、行動網路與外網端到端延遲仍需實機驗收，不能以合成影像視為實車通過。

## English

Update both `carrot-wip` and the IIS backend. Pair from the native FormosaLink screen, then explicitly enable **Carrot web** on the device while parked with ignition off. The portal opens the device's existing Carrot web in its own tab; native validation and confirmations remain active. This separate grant defaults off. Per-device paths isolate routing and browser preferences, while owner/session checks, signed outbound WSS and device-side parked/consent checks protect the connection. Upload requests are limited to 8 MiB; downloads stream with Range support. Use FormosaLink Live cameras for ultra-wide/cabin video: continuous MJPEG, target 8 fps, up to 640×360, no audio. The gateway does not supply WebRTC TURN/UDP forwarding. Existing accounts, pairings and the SQLite schema are preserved. Run the PowerShell command above on the IIS host and verify both health feature flags. Physical C3X/C4 cameras, load and external-network behavior remain to be validated.
