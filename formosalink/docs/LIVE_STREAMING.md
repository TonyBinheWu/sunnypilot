# FormosaLink 0.8.0 — 即時影像 / Live video / ライブ映像

## 繁體中文

超廣角與車內鏡頭改用持續的 WebSocket MJPEG 串流，目標每秒 8 格、最大 640×360，保留長寬比。裝置持續使用同一個 FFmpeg 編碼程序，透過已配對的自架 FormosaLink 傳送至手機，不再每兩秒擷取一次或由網頁輪詢照片。這是連續 MJPEG 影像串流，沒有音訊；不是 H.264/WebRTC，也不宣稱固定延遲或 30 fps。實際幀率取決於裝置、相機及網路，兩個分頁可同時選擇不同鏡頭。

### 連線與自架

- 拓樸：裝置 camerad → 唯讀 VisionIPC → 單執行緒、nice 10 的持續 FFmpeg → WSS/443 → IIS ARR → 本機 Python 影音 relay → 同一網站的登入手機。服務與影像均自架，不使用外部 STUN/TURN、影音雲端、CDN 或公有直播網址。單一 Python worker 為必要條件；不能直接加 workers 做負載平衡。
- 網際網路沿用 `https://formosapilot.dinglu-t.com` 與現有有效憑證、路由器 TCP 443。區網使用相同網址：路由器須支援 NAT loopback，或在內部 DNS 將這個名稱解析到 `192.168.20.145`。沿用相同網址才能保留 OAuth callback、cookie、裝置 origin 及 TLS 驗證。沒有額外公開 Python 8765、相機或 UDP 通訊埠；也不是裝置 IP 直連。
- 若使用另一個自架網域，需一致更新伺服器 origin、IIS 靜態 `web.config` 的 `connect-src` WSS 網域、OAuth callback、憑證與裝置配對設定。不要關閉 TLS 驗證。
- IIS 需 ARR、URL Rewrite 及 WebSocket Protocol。更新腳本會在停止既有後端前啟用 Windows 的 WebSocket 功能；若 Windows 要求重啟，腳本會保留原服務並明確要求重新啟動主機後重跑。若管理者曾另外停用本站 `system.webServer/webSocket`，請在本站設定啟用。反向代理必須保留 Host、Origin、Cookie 與 Upgrade/Connection headers。
- `wss://formosapilot.dinglu-t.com/api/v1/media/probe` 是不含裝置資訊的公開傳輸檢查，應收到 `{"service":"FormosaLink","transport":"wss-mjpeg-v1","fps":8}` 後正常關閉。只有 health 成功而 probe 失敗，代表 IIS／代理升級仍需排除；不會退回低頻照片假裝串流成功。

### 權限、回壓與行車功能

- 網頁只顯示已登入所有者的裝置。觀看 WebSocket 嚴格驗證 Host、Origin 與 HttpOnly session；每次傳送前重查帳號、所有權及撤銷狀態。登出、撤銷或轉移所有權會中止。
- 裝置連線使用獨立 Ed25519 金鑰簽署 `media-stream` 握手，綁定鏡頭，驗證一次性 nonce；TLS 保護後續影格。只在所有者的 15 秒觀看租約有效時接受傳送。關閉頁面後不再續期，最晚約 15 秒停止，裝置背景輪詢約再 2 秒收尾。沒有密鑰或存取權杖放在 URL。
- 每個觀看端只保留最新一格，解碼後回覆 ACK 才傳下一格；慢速網路丟棄中間影格，不累積播放歷史。每個鏡頭最多 4 個觀看端、整體 64 個觀看端／32 個鏡頭上傳連線。來源與序號、影格大小、時效皆驗證；禁止跨鏡頭混流。無人觀看時編碼器停止。
- 影像只存伺服器 RAM，最多 3 秒，無自動錄影；按錄影才在瀏覽器本機保存最多 60 秒、3 段。傳輸及錄影均不含音訊。手機頁面進入背景會斷開觀看並停止錄影，回到前景重連。
- 唯讀既有 camerad 的 wide-road／cabin NV12，不修改共享影格。沿用 0.7.0 的短效相機程序條件，不寫入 IsDriverViewEnabled／IsLiveStreaming，不改 CAN、模型、控制器、IR 或行車狀態。兩路編碼均單執行緒、降低程序優先序，超時會關閉編碼器重試；雲端故障不影響行車服務。實機 CPU／溫度／掉格與行動網路須另驗收，不能用桌面測試宣稱已驗證行車效能。

### 部署與更新

先推送兩分支並發布 IIS 檔案，再於 IIS 主機以系統管理員 PowerShell 執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython
```

保留原帳號、管理者密碼、GitHub OAuth、配對與資料庫（schema 仍為 3）。不用重新輸入 Secret。健康檢查必須出現 `live-camera-stream-v1`，然後以 probe 確認正式 WSS 升級。裝置更新對應分支並重啟後，手機重新整理並開始觀看。0.7 裝置只有預覽上傳，不能提供新版串流；新版畫面會持續等待裝置更新。

### 驗證範圍

兩分支各通過 167 項 Python、37 項 Node 測試。C3X／C4 原生桌面環境每個分支各 31 項，共 124 項通過。這些數字不代表實車或完整閉迴路行車模擬已通過。

主機測試可重跑：

```sh
python -m pip install -r formosalink/requirements-test.txt
python -m pytest formosalink/tests -q
node --test formosalink/tests/*.test.mjs
```

完成原生依賴建構的 Linux 桌面環境可執行 `python -m unittest formosalink.tests.camera_ui_check -v` 驗證 IPC 與編碼器；其餘原生 UI 測試需搭配 C3X（BIG=1）／C4（BIG=0）配置和實際顯示環境。

- Python：所有權隔離、跨來源拒絕、nonce、防重播、租約、撤銷、影格驗證、最新一格回壓、持續連線。另以真正 loopback TCP/Uvicorn/WebSocket 驗證兩鏡頭連續傳送與超過舊 16 KB 限制的影格。
- Node：三語、串流 URL、切換鏡頭、舊連線回呼不混入新畫面、解碼 ACK、停止連線；原設定同步及導覽測試保留。
- C3X／C4 原生環境：合成 wide-road／cabin VisionIPC、帶 padding 的 NV12、裝置附帶 FFmpeg 持續編碼及程序回收，既有原生選單、QR、SIM 與相機租約檢查。使用桌面環境，不是實體硬體或完整實車驗證。
- 待實機：兩台型號的實體鏡頭、同時串流的行車負載與溫度、夜間車內畫面、Wi-Fi/SIM 切換，以及手機區網／外網端到端畫面。不要將合成影像標為實車通過。

## English

0.8.0 replaces the two-second previews with continuous WebSocket MJPEG video: target 8 fps, up to 640×360 per camera, original aspect ratio, ultra-wide and cabin. Persistent single-threaded nice-10 FFmpeg encoders read existing VisionIPC without changing camera buffers or driving controls. There is no audio or H.264/WebRTC. Actual frame rate and latency depend on the device and network.

All video stays on your self-hosted IIS/ARR + one-worker Python relay over HTTPS/WSS 443. No hosted media service, STUN/TURN, public device port or cloud recording is needed. LAN uses the same authenticated domain and valid certificate through split DNS (`192.168.20.145`) or NAT loopback; Internet uses the existing public HTTPS endpoint. For a custom domain, align server origin, device pairing, OAuth, TLS and the static IIS CSP WSS authority.

Run the host setup command above. It installs the Windows WebSocket feature before stopping the existing backend and reports any required host reboot. Existing accounts, credentials, OAuth, pairings and database schema 3 remain intact. Health must advertise `live-camera-stream-v1`; the public `/api/v1/media/probe` WebSocket verifies the real proxy upgrade without exposing media. Update/reboot both device branches and refresh the phone. Old 0.7 camera uploads cannot feed the new stream viewer.

Viewers require same-origin authenticated ownership, rechecked before each delivery. Devices use signed, replay-protected camera-bound handshakes over verified TLS. Owner leases last 15 seconds and expire after viewing stops. Latest-only queues and decode ACKs prevent backlog; invalid, stale, wrong-camera and out-of-order frames are rejected. Limits: 4 viewers/camera, 64 total viewers, 32 publishers. Hidden tabs stop recording and disconnect, reconnecting in the foreground. Frames are RAM-only for at most 3 seconds; explicit browser-local recordings remain limited to 60 seconds and 3 clips.

Tests cover authorization/revocation, real loopback WebSocket flows, browser lifecycle and both native UI profiles with synthetic IPC and bundled FFmpeg. Real C3X/C4 camera images, driving resource use, temperatures, cellular handoff, night imaging and LAN/WAN phone acceptance remain hardware validation tasks. Cloud failure must not gate driving; model/controller/CAN/IR and driving flags remain untouched.

## 日本語

0.8.0 では約2秒ごとの静止画を、継続する WebSocket MJPEG 映像に変更します。超広角・車内の両方に対応し、目標毎秒8フレーム、最大640×360、元の縦横比を保持します。単一スレッド・nice 10 の FFmpeg を継続利用し、既存 VisionIPC を読み取り専用で取得します。音声や H.264/WebRTC は含みません。実際の速度と遅延は本体と通信環境によります。

IIS/ARR と単一 worker の Python 中継を自前で運用し、HTTPS/WSS 443 を使用します。外部映像サービス・STUN/TURN・本体への公開ポートは不要です。LAN でも同じドメインと有効な証明書を使用し、内部 DNS を `192.168.20.145` に向けるか NAT loopback を利用します。別ドメインの場合は origin・OAuth・本体登録・証明書・IIS CSP の WSS 設定を統一してください。

上記の PowerShell コマンドで更新します。既存サービスを停止する前に Windows WebSocket 機能を導入し、再起動が必要なら案内します。アカウント・OAuth・登録・データベース（schema 3）は保持します。health の `live-camera-stream-v1` と公開 WebSocket `/api/v1/media/probe` を確認し、本体の対応ブランチ更新・再起動とスマートフォンの再読み込みを行います。旧0.7のアップロードでは新しい配信画面を利用できません。

所有者のログイン・Origin・権限を継続確認し、本体は署名・nonce 付きのカメラ別握手を使用します。視聴リースは15秒で失効します。最新1フレームのみを保持し、描画後の ACK により遅い回線の履歴蓄積を防ぎます。各カメラ4人、全体64視聴・32送信に制限します。背景タブは切断して録画停止し、前景で再接続します。映像は最大3秒の RAM のみ、明示的な録画はブラウザー内の60秒・最大3件です。

権限・失効・実 TCP/WebSocket・画面ライフサイクル・C3X/C4 原生プロファイルの合成 IPC／付属 FFmpeg を検証します。実機映像、走行中の負荷・温度、SIM切替、夜間映像、LAN／外部回線のスマートフォンは別途実機確認が必要です。走行のモデル・制御・CAN・IR・状態設定は変更せず、クラウド障害で走行処理を停止しません。
