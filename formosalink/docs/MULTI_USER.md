# 多用戶與 GitHub 登入 / Multi-user access / 複数ユーザー

## 已實作：GitHub 登入與用戶隔離

目前網頁僅提供 GitHub 登入，配對請使用 [裝置 QR 流程](QR_PAIRING.md)。正式既有管理者已完成 GitHub 連結並保留原裝置。原密碼 API 僅保留供主機管理／復原，網頁不顯示密碼欄位。

新版使用 GitHub 數字 ID 識別用戶，username 僅供顯示。OAuth scope 為空，只取公開身分，不索取儲存庫權限。Token 僅用於當次 `/user` 驗證，不保存。配對會設定登入者為擁有者；清單、監看及撤銷均由後端限制為自己的裝置，管理者也沒有跨用戶讀取特權。裝置繼續使用獨立 Ed25519 身分回報。

### IIS 啟用

1. 在 [GitHub OAuth Apps](https://github.com/settings/developers) 建立 **FormosaLink**。Homepage URL：`https://formosapilot.dinglu-t.com/`。Authorization callback URL：`https://formosapilot.dinglu-t.com/api/v1/auth/github/callback`。不需啟用 Device Flow。
2. 在 IIS 主機以系統管理員開啟 PowerShell 執行：

   ```powershell
   powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython -ConfigureGitHub
   ```

3. 在主機以 輸入 Client ID，並在 Windows 密碼視窗使用「貼上 Secret」按鈕輸入 Client Secret，請勿貼到聊天。資料存於私有 `C:\ProgramData\FormosaLink\github.json`，原密碼不重設。成功後 `/api/v1/auth/me` 的 `github_enabled` 為 true，health 有 `device-ownership` 及 `database_version: 3`。僅複製網站檔案不會更新執行中的私有後端。
4. 既有正式管理者已透過明確連結流程驗證 GitHub 身分，原裝置保留在同一管理者下。一般 GitHub 登入建立獨立帳號，不會自動合併。已屬於另一用戶的 GitHub 身分不能被管理者連結接管。
5. 其他用戶在裝置產生 QR、用手機掃描，再以 GitHub 登入並確認即可。配對碼與指紋自動帶入，不需手動輸入。

### 遷移與回復

第一次啟動先備份至私有資料目錄的 `formosalink.sqlite3.before-v2.sqlite3`，再於交易內將 SQLite v1 升級為 v2。原配對／撤銷裝置及登入階段歸屬 `local-admin`；ID、金鑰、名稱與回報保留。待配對裝置在配對時才設定擁有者。第一位 GitHub 用戶不會取得既有裝置。

回復前須停止排程及確認服務 Python 已結束，另存目前 v2 資料庫，再還原備份與對應舊程式；回復會失去升級後新增的帳號與配對。不要在服務執行中覆蓋 SQLite。若 v1 與升級備份同時存在，程式會停止要求人工檢查，避免覆蓋備份。

OAuth 使用 10 分鐘有效、一次性且綁定瀏覽器的 state 與 S256 PKCE。管理者連結另綁定開始時的有效管理者 session，登出即使連結無效。登入 cookie 為 HttpOnly/Secure/SameSite=Strict；OAuth cookie 為 Lax，限定 callback 路徑。變更 API 驗證 Origin。後端關閉 access log；請在 IIS Logging / Select Fields 取消 `URI Query (cs-uri-query)`，CDN／代理也應遮罩查詢參數，避免記錄短效 OAuth code。勿開啟 HTTP debug log。

單一 Python worker 限制維持。增加 worker 前須導入共用連線狀態及路由。已登入用戶、裝置回報與原管理者密碼登入不需持續連線至 GitHub。

### English

GitHub numeric IDs map to separate users; mutable usernames are display only. Empty scope requests public identity without repository access. Tokens are used once and never persisted. Pairing assigns the authenticated owner; all listing, monitoring and revocation are owner scoped. Administrators do not get cross-user access.

Create the FormosaLink OAuth App with the homepage and exact callback above. Run the command on the IIS host as administrator, adding `-Language en` for English prompts. Enter Client ID and hidden Client Secret locally; credentials stay outside the web root. The original password API is retained for host administration and recovery, but is not shown on the website. The production administrator has already completed explicit GitHub linking and retained existing devices. Other GitHub users start with no devices and pair by scanning the device QR. Existing separate accounts are never automatically merged.

Schema v1 is backed up to `formosalink.sqlite3.before-v2.sqlite3` before transactional migration to v2. Existing devices, keys and sessions remain with `local-admin`. Stop the service before restoring the backup and matching old code; preserve the current DB first. Restoration loses post-migration changes. Existing migration backups require inspection before retrying a v1 migration.

State is browser-bound, one-use and expires in ten minutes; S256 PKCE is required. Administrator linking requires the initiating session to remain valid. Backend access logs are disabled; disable IIS `cs-uri-query` and redact proxy/CDN queries. Keep one worker until shared device connection routing is available. Existing sessions, device ingestion and password fallback do not require GitHub availability.

### 日本語

GitHub の数値 ID ごとに独立したユーザーを作成し、ユーザー名は表示専用です。scope は空で、公開情報のみ取得し、トークンを保存しません。登録・一覧・監視・解除はサーバーで所有者を確認します。管理者にも他ユーザーのデバイスは表示しません。

上記の Homepage と正確な callback で FormosaLink OAuth App を作成します。IIS ホストで上記コマンドに `-Language ja` を加えて実行し、Client ID と非表示の Client Secret を本体で入力してください。設定は Web ルート外に保存し、元のパスワードは維持します。Web ページは GitHub ログインのみです。パスワード API は本体管理・復元用に保持します。本番管理者は GitHub 連携を完了し、既存デバイスを維持しています。他のユーザーは独立アカウントを作成し、デバイス QR から登録します。自動統合はしません。

v1 は `formosalink.sqlite3.before-v2.sqlite3` にバックアップ後、トランザクションで v2 に移行します。既存デバイス・鍵・セッションは `local-admin` に保持します。復元前にサービスを停止し、現在の DB を保存し、バックアップと対応する旧コードを戻してください。移行後の変更は失われます。v1 と既存バックアップがある場合は手動確認が必要です。

OAuth はブラウザーに結び付けた一回限りの state、10 分の期限、S256 PKCE を使用します。管理者連携は開始時の有効な session が必要です。IIS の `cs-uri-query` を無効にし、CDN／プロキシもクエリーを記録しないよう設定してください。共通接続管理を実装するまでは単一ワーカーです。既存セッション・デバイス通信・パスワードログインは GitHub が停止しても利用できます。

Reference: [GitHub OAuth web application flow](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps).


0.3.0 新增設定通道與 v2→v3 備份遷移；詳見 [停車設定](OFFROAD_SETTINGS.md)。擁有者隔離也套用於裝置資訊、設定目錄、寫入排程與回執，管理者不會取得其他用戶裝置的權限。
