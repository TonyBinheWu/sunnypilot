# FormosaLink QR 配對 / QR pairing / QR 登録

## 繁體中文

網站只顯示 GitHub 登入。管理者密碼、手動配對碼及指紋輸入欄位已移除；原管理者身分、既有 GitHub 連結及配對資料保留。

1. 裝置更新至對應的 `hkg-enhanced` 或 `ccnc-port` 後，停車並開啟 **設定 → 裝置 → FormosaLink**。C3X 是新增按鈕，C4 是新增卡片。
2. 點「產生配對 QR」。此操作是本機對唯讀監看的明確啟用；裝置需可連線到 HTTPS 伺服器。第一次使用會建立獨立 Ed25519 身分，保存在 `/data/formosalink`，不使用 comma 或 sunnylink 的金鑰。
3. 用手機相機掃描 QR。手機登入 GitHub 後會自動開啟確認畫面，只需確認裝置名稱並按「確認並配對」。不需輸入配對碼或指紋。
4. 配對完成後 agent 開始回報；裝置畫面會顯示成功。關閉配對畫面不會停止已明確啟用的唯讀 agent。若要停用，於同一裝置畫面點「停用監看」。網頁撤銷則會立即阻止伺服器接受該裝置後續回報。

QR 十分鐘有效、只能使用一次。重新產生會使舊 QR 失效；到期請在裝置重建並重新掃描。請勿分享 QR 或配對連結。已配對的裝置不會再顯示可供其他帳號認領的 QR；撤銷後須明確建立新身分才能重配。

配對資料放在網址 `#fragment`，不放 query string，網站讀取後立即清除網址中的憑證。登入往返只在該分頁的 `sessionStorage` 暫存；完成或到期即清除，不使用 localStorage 儲存配對資料。如果瀏覽器禁止暫存，先登入 GitHub，再掃描一次即可。畫面只隱藏輸入，不移除後端的短效碼、指紋比對、簽章與擁有者檢查。

裝置透過 `POST /api/v1/agent/status` 以 Ed25519 簽章查詢自己的 `pending/paired/revoked` 狀態，含 nonce／時間窗防重放，不取得用戶資料，也不輪替正在顯示的 QR。網路請求在背景執行；QR 繪製、參數變更在 UI 執行緒處理。行車中禁止產生 QR 或改變監看開關，關閉／停用後的舊背景結果不得重新啟用 agent。

自架其他網域時，先於本機使用 CLI 建立該網域的獨立身分，之後 UI 沿用已設定的 origin：

```sh
python -m openpilot.sunnypilot.formosalink.cli --lang zh-TW pair --url https://your-link.example.com
```

IIS 更新後需在主機執行一次下列指令載入新增的簽章狀態 API。**不用重新輸入 GitHub Secret 或管理者密碼**，不要加 `-ConfigureGitHub`：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython
```

成功後 health 必須含 `qr-pairing`。網站舊有密碼 API 保留作為主機管理與復原介面，但日常網頁不提供密碼登入。正式管理者已完成 GitHub 連結；一般用戶以自己的 GitHub 帳號與裝置 QR 配對。

## English

The website uses GitHub sign-in only. Password login and manual code/fingerprint inputs are removed from the page; existing identities, GitHub links and devices are retained.

While parked, open **Settings → Device → FormosaLink** on the matching updated branch. Select **Show pairing QR**, an explicit local opt-in to read-only telemetry. Scan with your phone camera, sign in with GitHub and confirm the device name. Pairing credentials are filled automatically. Use **Disable monitoring** locally to stop the optional agent. Revocation on the website prevents further server ingestion.

QR codes are single-use and expire in ten minutes. Generating a new code invalidates the previous one. Do not share QR codes or pairing links. Credentials stay in the URL fragment, are removed from the address bar immediately, and survive the OAuth round trip only in this tab's sessionStorage. They are cleared after pairing or expiry. If storage is blocked, sign in first and scan again. Backend fingerprint verification, device signatures and account ownership checks remain mandatory.

The device polls a signed, replay-protected status endpoint without rotating the QR or exposing account details. Network work runs in a background thread. Onroad operations and late-result re-enabling are blocked. UI and status changes do not alter driving controls. Custom self-hosted origins can be initialized with the CLI above.

After copying the IIS runtime package, run the host command above **without `-ConfigureGitHub`**. Existing OAuth credentials and admin data are retained; health must include `qr-pairing`. Physical devices must install their updated branch before the QR entry appears. Native Linux C3X/C4 profile tests are not physical-device or vehicle acceptance tests.

## 日本語

Web ページは GitHub ログインのみです。パスワード、コード、フィンガープリントの手動入力欄は削除し、既存の管理者・GitHub 連携・デバイスは保持します。

対応ブランチへ更新後、停車中に **設定 → デバイス → FormosaLink** を開き、「登録用 QR を表示」を選択してください。これは本体での読み取り専用監視の明示的な有効化です。スマートフォンで QR を読み取り、GitHub ログイン後にデバイス名を確認して登録します。情報は自動入力されます。停止する場合は本体で「監視を停止」を選択します。Web で登録解除した場合、サーバーは以降のデータを受け付けません。

QR は 10 分間有効で 1 回限りです。再発行すると古い QR は無効になります。QR や登録リンクを共有しないでください。情報は URL の fragment に格納し、読み込み後にアドレスから削除します。OAuth の往復では当該タブの sessionStorage のみ使用し、完了または期限切れ時に削除します。保存できない場合は先にログインしてから再度スキャンしてください。サーバーの署名、フィンガープリント、所有者確認は維持します。

本体は署名・リプレイ保護付き API で状態のみ確認し、QR を更新したりアカウント情報を取得したりしません。通信はバックグラウンドで実行します。走行中の登録・切替と、停止後の古い応答による再有効化を防ぎます。

IIS パッケージ更新後、上記コマンドを **`-ConfigureGitHub` なし**で本体上で実行してください。既存の認証情報は保持し、health の `qr-pairing` を確認します。デバイスも対応ブランチへの更新が必要です。Linux 上の C3X/C4 profile 検証は実機・実車の動作保証ではありません。


0.3.0：配對維持監看權限；如需停車設定，須另在本機開啟「停車遠端設定」。操作與三語說明見 [OFFROAD_SETTINGS.md](OFFROAD_SETTINGS.md)。
