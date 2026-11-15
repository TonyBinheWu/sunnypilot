# FormosaLink 自架遠端服務 / Self-hosted remote service / 自己ホスト型リモートサービス

## 繁體中文

裝置的 FormosaLink 主選單、「裝置」QR 配對，以及 C3X 首頁雲端卡片，均使用獨立 FormosaLink 身分與通訊協定，預設伺服器為 https://formosapilot.dinglu-t.com。已有自架身分沿用原 origin、Ed25519 金鑰及配對；沒有默默換身分、移轉 Sunnylink 帳號或自動同意遠端設定。

舊平台的註冊、遠端 daemon、統計、雲端備份及 uploader 在程序管理器中強制停用；UI 不再建立舊帳號狀態輪詢器或顯示舊同意／贊助／配對頁。啟動時關閉舊開關，僅在 PID、命令列模組及獨立程序群組皆符合時終止殘留的舊遠端 daemon，其他 SSH 或原生 comma 程序不會被終止。舊憑證保留但不使用。舊平台的備份／上傳功能沒有偽裝成已移植到新協定。

手機透過 QR 與 GitHub 登入自架 FormosaLink；遠端設定仍需本機允許、停車條件、逐項衝突檢查及裝置回讀。側欄僅在自架伺服器確認過遙測且回覆未過期時顯示上線；沒有舊 ping 的替代顯示。sunnylink.ai／sunnypilot.ai 及子網域不能作為 FormosaLink 身分或通訊端點，連線失敗不回退舊服務。原生行車、CAN、控制器、模型、GNSS 及 openpilot 基礎服務未變更。

更新對應分支後必須重新啟動裝置，確認主選單僅有 FormosaLink 配對服務；已配對使用者不必重新建立身分。更新前未配對的裝置，停車後按「產生配對 QR」，手機掃描、登入 GitHub 並確認。自架平台既有 API 相容，本批不變更資料庫結構或要求管理者密碼。實體裝置的上線狀態與網路恢復仍需實機驗收。

## English

FormosaLink settings, device QR pairing and the C3X home cloud card use the independent FormosaLink protocol and identity, defaulting to https://formosapilot.dinglu-t.com. Existing self-hosted origin, private key, pairing and local consent are retained. Old Sunnylink accounts and permissions are not transferred automatically.

Legacy registration, remote daemon, statistics, cloud backup and uploader processes are disabled in the manager, irrespective of persisted old flags. The UI does not instantiate the old account poller or display its consent, sponsorship or pairing pages. Startup retires only a verified legacy supervisor in its own process group; unrelated SSH and native comma processes remain intact. Old credentials remain stored but inactive. Legacy cloud backup/upload features have not been reimplemented under a different name.

QR/GitHub pairing, monitoring and parked settings use the self-hosted service. Remote setting guards, conflict checks and device readback remain required. Online status requires a fresh telemetry acknowledgement from the same server. Old Sunnylink/Sunnypilot service domains and their subdomains cannot be used as FormosaLink endpoints; there is no fallback. Driving, CAN, controllers, models, GNSS and core openpilot services are unchanged. Update and reboot the matching device branch; existing users do not need to regenerate identity. No database migration or administrator password change is required. Physical device acceptance remains pending.

## 日本語

FormosaLink のメニュー・デバイス QR 登録・C3X ホームカードは独立した ID とプロトコルを使い、標準の接続先は https://formosapilot.dinglu-t.com です。既存の自己ホスト先・鍵・登録・本体の許可は保持し、旧アカウントや許可を自動移行しません。

旧サービスの登録・リモート daemon・統計・クラウドバックアップ・アップロードをプロセス管理で停止し、旧ポーリング・同意・スポンサー・登録画面を表示しません。起動時に確認済みの旧専用プロセス群のみ終了し、他の SSH と comma の基礎サービスは維持します。旧クラウド機能を移植済みと表示することはありません。

QR と GitHub 登録、監視、停車中の設定は自己ホスト先を使用し、競合検出と本体の読み戻しを維持します。オンライン表示には同じサーバーからの新しい確認応答が必要です。旧サービスのドメインには接続せず、失敗時のフォールバックもありません。走行・CAN・制御・モデル・GNSS は変更しません。対応ブランチを更新して再起動してください。既存の登録・データベース・管理者パスワードの変更は不要です。実機での通信確認は別途必要です。
