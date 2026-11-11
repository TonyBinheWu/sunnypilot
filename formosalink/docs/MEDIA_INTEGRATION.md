# FormosaLink 影音整合 — 0.6.0，第 1 階段

## 繁體中文

目標是完整提供 CommaView 類型的觀看、錄影、行程、定位與直播功能，使用自己的 FormosaLink 帳號、配對及自架服務。本版先交付可運作的 HTTPS 預覽中繼、明確啟動的發送器及瀏覽器錄影。**尚未接取 C3X／C4 實車相機，也未完成低延遲串流或完整道路疊圖。**

| 階段 | 範圍 | 目前進度 |
| --- | --- | --- |
| 1 | 裝置簽章影像、所有者隔離、自架 HTTPS 中繼、觀看、速度文字、全螢幕／PiP、本機短片回放下載 | 程式與本機 DEMO 驗證；正式 IIS 需更新後端 |
| 2 | C3X／C4 相機 adapter、裝置本機允許／停止、硬體編碼及低延遲影像、需要時自架 TURN | 未完成，需實機負載與斷線驗收 |
| 3 | 與兩分支匹配的道路／車道／前車／警示疊圖及校正 | 未完成；目前只有獨立文字 HUD，不是原生行車畫面重製 |
| 4 | 錄影庫、行程統計、GPS／停車位置及個別同意與保留政策 | 未完成；本版不收集 GPS 或行程 |
| 5 | 自架對外直播閘道與車機顯示驗證 | 未完成；本版不連 YouTube／第三方直播服務 |

### 架構與限制

```
明確啟動的 JPEG 發送器
  → Ed25519 簽章 HTTPS POST /api/v1/agent/media
  → 既有 IIS 443 → Python 單 worker RAM 中繼
  → 已登入且擁有該裝置的瀏覽器 HTTPS GET
  → Canvas 預覽／MediaRecorder 本機短片／下載
```

這是低頻率 JPEG 預覽，不是 20／30 FPS 視訊。發送工具最多約每秒 2 次，預設 60 秒；影像上限 1280×720、180,000 bytes，簽章訊息上限 262,144 bytes。中繼最多保留 32 台裝置的最新畫面；這是記憶體上限，不是已驗證同時觀看容量。既有 API 速率限制仍有效，多人負載需另行測試。

伺服器不建立影片檔或影像歷史，只有目前畫面與 TTL。來源時間必須新鮮、序列遞增且 nonce 不可重播；超過 3 秒不再提供，過期 RAM 項目在下一次中繼請求清理。瀏覽器另有 250ms 鮮度檢查，停止繪製舊畫面並停止錄影；慢於 3 秒的預覽回應不採用。每次觀看都核對帳號、配對與所有權，撤銷後不能繼續取得影像。仍需接受網路延遲及畫面可能不連續的限制。

錄影是瀏覽器 MediaRecorder 的本機短片，最多每段 60 秒／約 16 MiB、分頁內最多三段；可直接回放及下載。不自動上傳影片，離開影音頁、切換裝置、重新整理、登出會釋放片段，請先下載。切換語言保留觀看及片段。支援的容器／PiP／全螢幕能力依瀏覽器，無支援時停用或顯示提示；不是可靠行車記錄器。

本版沒有改動行車程序、車型、控制器、安全策略或相機 manager；沒有自動安裝第三方 runtime，也不啟動原生相機／編碼器。APK 僅供功能盤點，沒有重新發布 APK、其素材、模型或反編譯程式。來源 APK：`CommaView-0.0.166-alpha.9.apk`，SHA-256 `aeadb0fafa0c0acea1650e3a148c732c2f29840c21f471fa34feee3d0db4cedd`。參考 [官方功能](https://commaview.com/) 與 [App/runtime 架構](https://commaview.com/docs/install)。

### 發送端驗證

測試必須使用自己的已配對身分；私鑰不貼到聊天或瀏覽器。

```powershell
python -m openpilot.sunnypilot.formosalink.media_agent --state-dir <已配對身分目錄> --jpeg-file formosalink/tests/fixtures/media-demo.jpg --demo --allow-upload --seconds 60
```

`--allow-upload` 是這個手動工具的明確傳送開關，不會由原生 FormosaLink agent 自動啟動。DEMO 圖與速度不代表實車。沒有 `--demo` 時，讀取本機 JPEG 檔案的 mtime，超過 3 秒便拒絕；外部檔案來源需持續以原子更名更新。此檔案入口不是已完成的原生相機 adapter。

### IIS 更新

沿用同一個 HTTPS 網站，不需額外影音帳號、外部雲端或新防火牆連接埠。區網可由內網 DNS 將 `formosapilot.dinglu-t.com` 指向 `192.168.20.145`，仍使用相同 HTTPS 網址與憑證；外網沿用現有 443 入口。這不提供斷網時的獨立裝置熱點服務。

發布套件後，在 IIS 主機以系統管理員 PowerShell 執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython
```

原帳號、OAuth、配對、資料庫 schema 3 保留，無須輸入密碼。啟動檢查需看到 `media-preview-v1` 才顯示成功。IIS requestFiltering 上限改為 524288，Python 保持各路由獨立上限；一般 API 仍為 16384。CSP 新增同源／blob 影片，沒有任意外部來源。更新前網頁會顯示影音後端待更新，不會偽裝已有實車影像。

## English

Phase 1 adds a self-hosted, owner-scoped, device-signed HTTPS JPEG relay, an explicitly launched file/demo publisher, a trilingual preview and browser-local recording/playback/download. It does not yet capture native C3X/C4 cameras, reproduce native road overlays, collect GPS/trips or broadcast externally. Those remain the staged roadmap above.

Frames are bounded and expire after three seconds; only the latest frame is held in single-worker RAM and expired entries are pruned on relay access. No server video archive is created. Browser clips are limited to 60 seconds, approximately 16 MiB and three in-memory clips; download before leaving the page. Background/stale/disconnected viewing stops recording. Browser feature support varies. Driving processes and hardware camera/encoder configuration are unchanged.

Publish to the existing IIS site, then run the host setup command above. Credentials, pairings and schema 3 remain. Health must advertise media-preview-v1. LAN and internet use the same HTTPS origin; optional internal DNS points that origin to the IIS LAN address. This phase needs no TURN, external video cloud or additional public port. Real hardware and network-performance acceptance remain outstanding.

## 日本語

第1段階では、自架 HTTPS JPEG 中継、装置署名と所有者確認、明示起動のファイル／DEMO 送信、3言語のプレビューとブラウザー内の短時間録画・再生・保存を提供します。C3X／C4 実機カメラ、道路オーバーレイ、走行統計、GPS／駐車位置、外部配信は未実装です。

最新画像のみを RAM に保持し、3秒で配信対象外となり、次のアクセスで期限切れを除去します。サーバーの動画保存はありません。録画は各60秒・約16MiB・最大3件で、ページを離れる前に保存してください。背景・期限切れ・切断時は録画を停止します。ブラウザーの対応状況に依存し、運転制御や相機／エンコーダー設定は変更しません。

既存 IIS に配布後、上記コマンドでホストの Python を更新してください。認証情報、登録、schema 3 は維持します。LAN／インターネットとも同一 HTTPS を使用し、この段階では TURN や外部映像クラウド、新しい公開ポートは不要です。実機・ネットワーク負荷の検証は別途必要です。
