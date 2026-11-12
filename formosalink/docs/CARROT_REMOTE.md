# CarrotPilot 雲端網頁與雙鏡頭 LIVE

本分支 `carrot-wip` 接入既有 FormosaLink。入口為 [FormosaLink](https://formosapilot.dinglu-t.com)，以原有 GitHub 帳號與獨立裝置 QR 配對使用。已存在於 `/data/formosalink` 的身分可沿用；車機與 IIS 都須更新。

## 車機設定

1. 更新本倉庫 `carrot-wip`，安全停車後重新啟動。
2. C3X 在「裝置 → FormosaLink」開啟配對；C4 在「設定 → FormosaLink」開啟。
3. 掃描 QR，於手機登入 GitHub，核對並完成配對。
4. 要使用原生 Carrot 網頁時，在車機配對畫面將「遠端 Carrot 網頁：關」切換成「開」。此權限預設關閉；本分支沒有使用 sunnypilot 的「停車遠端設定」開關。
5. 車機須保持網路連線。遠端網頁需要停車熄火、有效的裝置狀態與 Panda 狀態；資料過期時會關閉通道。

本機參數 `FormosaLinkEnabled` 預設開啟背景連線，但仍需配對；`FormosaLinkRemoteWeb` 預設關閉，控制原生 Carrot 網頁通道。Carrot 的 FormosaLink 健康面板只提供讀取，設定操作使用原生 Carrot 網頁；沒有套用 sunnypilot 的車型設定 schema。原有 `FormosaLinkRemoteSettings` 不會自動授予完整網頁權限。

## 遠端操作 Carrot 網頁

登入 FormosaLink，在 `carrot-wip` 裝置卡片選「遠端 Carrot 網頁」，於新分頁開啟原生介面。可使用既有的繁中設定搜尋、參數調整、說明、備份與工具；原生 Carrot 自己的驗證、生效時機與確認流程仍會執行。完整網頁也包含原有終端與維護能力，因此這是完整網頁授權。

網站 `0.8.4` 另提供「Carrot 設定」按鈕，可直接進入該裝置的原生設定頁；「裝置資訊」內也有相同入口。搜尋、設定詳細說明及儲存均在原生頁面操作，不使用 sunnypilot 的空白設定目錄。首次使用仍先完成原生介紹流程。入口僅指定此分頁的起始頁，不改寫車機或瀏覽器儲存的首頁偏好，也不會自動開啟遠端授權。

車機需更新本次 `carrot-wip` 才會自動切至設定頁；較舊版本仍可開啟原生網頁，再手動選「設定」。網站 `0.8.5` 同時辨識車機回報的 `carrot-wip` 與 `origin/carrot-wip`，並修正本機指南經雲端讀取時省略登入憑證的問題。原生設定列的繁中標題與短說明修正需更新車機；不改變參數值或生效時機。

**已使用 setup-server.ps1 安裝的 IIS 主機：**服務從網站外的 `C:\ProgramData\FormosaLink-code` 載入私有副本。只更新 `App_Data/server-package` 並不會更新正在使用的 bridge。在 IIS 主機以系統管理員 PowerShell 執行以下指令，同步這一個檔案即可；工具先備份並核對雜湊，不重啟服務、不更動帳號、配對或設定。使用自訂資料目錄時需附上原本的 `-DataDirectory`。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\update-web-bridge.ps1"
```

完成後重新載入遠端 Carrot 分頁。此同來源憑證只用於 FormosaLink 所有者驗證；閘道不會把 FormosaLink cookie 傳給車機，外部指南請求仍沿用原本的憑證政策。

每個分頁固定綁定一台裝置。兩台裝置同時開啟時，HTTP、WebSocket、靜態資源與瀏覽器偏好各自路由；沒有共用的「目前裝置」cookie。FormosaLink cookie 不會轉送給車機；Carrot 自己的 Bearer 授權可沿通道傳遞。

通訊路徑為手機 HTTPS/WSS → IIS → FormosaLink relay → 車機主動建立的已簽署 WSS → 固定 `127.0.0.1:7000`。不需公開車機 7000 埠。伺服器每次請求及串流傳送都重查登入與裝置所有權，裝置則檢查本機授權與停車狀態。撤銷授權、登出、解除配對或開始行車會關閉通道；已送達原生工具的操作仍依該工具的執行結果處理。

HTTP 上傳的整個請求內容上限為 8 MiB。下載支援串流與 Range，傳輸採分段確認及回壓；每台裝置最多 16 個同時處理的請求／WebSocket。離線不會自動重送操作。Carrot 原生 WebRTC 的 ICE／NAT 限制仍存在；HTTP/WebSocket 通道不會轉送 UDP。遠端鏡頭請使用下面的 FormosaLink LIVE。

## 前廣角／車內鏡頭 LIVE

在裝置卡片選「雙鏡頭 LIVE」，或進入裝置工作區的「即時影像」。選擇「前廣角」或「車內」後開始觀看，可停止、全螢幕，並依瀏覽器能力使用子母畫面或本機錄影。兩個分頁可分別觀看不同鏡頭。

既有串流為連續 WebSocket MJPEG，目標 8 fps、最大 640×360、保留長寬比，不含音訊；沒有宣稱固定延遲或 30 fps。每路使用持續、單執行緒、低優先序的 FFmpeg，讀取既有 VisionIPC，不修改相機共享影格。Carrot 車內鏡頭使用其 `VISION_STREAM_DRIVER`，並兼容沒有 `uv_offset` 的 NV12 影格。

觀看需要登入所有者，短效租約最長 15 秒。關閉／背景化網頁或停止觀看後，租約到期便停止編碼；無人觀看時不持續上傳。最新影格與解碼確認限制排隊，資料過期會清除畫面。伺服器不自動保存影像；手動錄影只保存在目前瀏覽器。完整機制見 [LIVE_STREAMING.md](LIVE_STREAMING.md)。

## IIS 更新

### 按鈕重載或一直等待影像

- 若診斷顯示「連接雲端影像通道 (TypeError)」且雲端確認影格數為 0，請更新至修正 WebSocket 連線生命週期的版本並重啟車機。`websocket-client` 連線不提供直接的 `with` 介面，新版使用 `contextlib.closing` 確保正常啟用與關閉連線。既有 IIS 後端與 `0.8.2` 網頁可沿用。

- 若點車機「遠端 Carrot 網頁」後 UI 重載，請更新至修正 Carrot Params 寫入介面的版本並重新啟動。此按鈕只切換本機網頁授權，不應重新啟動 UI 或整台裝置。
- 在 FormosaLink 按「開始觀看」便會自動建立短效觀看租約、喚醒鏡頭並傳送；不需另外執行手動影像發送指令。等待期間請確認車機在線，亦可切換前廣角／車內鏡頭交叉檢查。
- 鏡頭時間戳使用包含休眠時間的 Linux 開機時鐘；接收端也必須使用相同時鐘。新版修正休眠後新影像被誤判無效的情況，仍會拒絕過期或未來影像。
- 更新車機並重新啟動後，關閉舊網頁再重新開啟。網站模組版本為 `0.8.3`；若仍看到「需先在來源端明確啟動發送」，表示仍載入舊頁面，請重新整理或清除該站快取。
- 若雲端已確認影格數持續增加、畫面仍黑，請檢查新版「瀏覽器收到影格數」「已顯示影格數」及瀏覽器錯誤／連線關閉代碼。收到影格卻未顯示時，新版會區分格式錯誤、過期、JPEG 解碼失敗、解碼逾時及繪圖失敗，不再全部顯示為 WebSocket 中斷。`0.8.3` 是網站修正，車機可沿用 `e985d699`，IIS 後端無須重啟。
- 網頁以同來源健康檢查的 HTTP `Date` 校準伺服器時鐘，並以瀏覽器單調時鐘推算影格年齡，避免電腦時鐘偏差讓新影像被丟棄。計算保留 HTTP 日期的一秒精度及請求來回時間之誤差界限；無法取得有效時間時重試，不關閉影格時效檢查。真正的 Chrome／Chromium 測試涵蓋正常時鐘、快／慢一天、兩個鏡頭的 JPEG 解碼與實際畫布像素，以及損壞 JPEG 的明確提示。
- 新版「即時影像」在畫面下方提供繁中分段診斷：觀看請求是否抵達、相機連接、影格等待、編碼、雲端連接及雲端確認影格數。狀態由車機透過既有已簽署的健康同步回報；超過有效期便顯示無法判定，不把「裝置在線」當成鏡頭正常。錯誤只回報類別或 HTTP 狀態碼，不上傳例外內容、影像或金鑰。
- 原生 openpilot WebRTC 訂閱既有 `livestream*EncodeData` 的 H.264 封包；本分支的原生 Carrot 網頁影像通道只提供道路鏡頭。FormosaLink 雙鏡頭目前仍使用 VisionIPC 加 MJPEG，以支援前廣角與車內鏡頭及既有 HTTPS/WSS 中繼。相機短暫無影格時會保留連線等待最多一秒，不再因單次 50 毫秒逾時就重建連線。測試已加入實際 Linux FFmpeg 的首幀與持續編碼，仍不等於實機驗收。
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

Portal 0.8.4 adds **Carrot settings** on the device card and information workspace. Enable the existing local **Carrot web: off → on** control while parked with ignition off; carrot-wip does not use sunnypilot's separate **Parked settings** switch. Settings, search and detailed help remain in the native web interface. Update the vehicle for direct settings-page navigation and Traditional row text; older devices can open the native home page and select Settings manually. The per-tab hint preserves saved home-page preferences and the first-run introduction. Portal 0.8.5 recognizes tracking-branch names and preserves owner authentication for local guides. Installed IIS services read a private runtime copy: run the bridge-only PowerShell updater above on the IIS host, then reload the remote tab. No backend restart or account/pairing/settings change is needed.

Update both `carrot-wip` and the IIS backend. Pair from the native FormosaLink screen, then explicitly enable **Carrot web** on the device while parked with ignition off. The portal opens the device's existing Carrot web in its own tab; native validation and confirmations remain active. This separate grant defaults off. Per-device paths isolate routing and browser preferences, while owner/session checks, signed outbound WSS and device-side parked/consent checks protect the connection. Upload requests are limited to 8 MiB; downloads stream with Range support. Use FormosaLink Live cameras for ultra-wide/cabin video: continuous MJPEG, target 8 fps, up to 640×360, no audio. The gateway does not supply WebRTC TURN/UDP forwarding. Existing accounts, pairings and the SQLite schema are preserved. Run the PowerShell command above on the IIS host and verify both health feature flags. Physical C3X/C4 cameras, load and external-network behavior remain to be validated.
