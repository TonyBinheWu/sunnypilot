# 多用戶與 GitHub 登入 / Multi-user access / 複数ユーザー

## 目前可用方式

0.1 是單一管理者、自架實例。每位使用者可各自部署一套，設定自己的密碼與裝置；不能共用本平台的管理者密碼。多人共用 `formosapilot.dinglu-t.com` 前，必須完成下列 GitHub 登入及權限改造。這份文件是下一階段設計，不代表目前已開放 GitHub 登入或公開註冊。

## 共用平台的必要改造

1. GitHub OAuth 登入：建立專用 OAuth App；預定 callback 為 `https://formosapilot.dinglu-t.com/api/v1/auth/github/callback`。Client secret 僅保存在伺服器私有設定，不進 Git、網站目錄或前端。使用一次性 state、明確的重新導向白名單與短效登入流程。
2. 使用穩定的 GitHub provider user ID 識別帳號，不能用可更名的 username 作為唯一身分。只要求登入必要權限，不要求讀取私人儲存庫或 SSH 權限。
3. 新增 users、sessions.user_id、devices.owner_id；所有裝置清單、回報讀取、配對、撤銷與日後設定 API 都在後端驗證擁有者，不能只靠前端隱藏其他裝置。
4. 保留獨立的裝置 Ed25519 身分與本機提出的配對碼。登入 GitHub 不等於取得裝置權限；使用者必須親自配對，裝置才屬於該帳號。
5. 現有管理者及裝置需明確遷移：使用原管理者驗證完成認領；禁止讓第一個 GitHub 登入者自動取得既有裝置。擁有者移轉與分享另建明確流程及稽核。
6. 登入憑證、OAuth token、device key 的用途分離。GitHub／Logto 登入、裝置認證與 GitHub SSH keys 是不同權限系統。
7. 開放註冊前，驗證兩個真實不同帳號無法越權讀取、配對或撤銷對方裝置，並驗證 CSRF、OAuth state 重用、登出、撤權與遷移回復。
8. 超出單程序部署時，將目前記憶體內的連線狀態移到共用訊息／狀態層，並規劃 PostgreSQL 遷移；不可直接增加 workers 後假設狀態與路由會自動一致。

sunnylink 公開前端使用 Logto SSO。可選擇自架 Logto 串接 GitHub，或在 FormosaLink 後端直接串接 GitHub OAuth；兩種方式都需要上述擁有權隔離，換一顆登入按鈕並不足夠。參考：[官方 sunnylink 前端](https://github.com/sunnypilot/sunnylink-frontend)。

## English

Release 0.1 is a private, single-owner instance. Other users can deploy their own instance with separate credentials. Do not share the administrator password. Central hosting requires GitHub OAuth, stable provider IDs, owner-scoped sessions and device authorization on every API. Device keys and explicit pairing remain independent from GitHub login. Migrate existing ownership only after verifying the current administrator; never grant existing devices to the first OAuth user. Keep secrets outside the web root/repository. Test cross-account isolation before enabling public signup. Multiple workers also require shared connection/state routing and an explicit database migration. GitHub login is not implemented by this design document.

## 日本語

0.1 は単一管理者のプライベートな自架環境です。他の利用者は各自の環境とパスワードで運用できます。管理者パスワードは共有しないでください。共用サイトには GitHub OAuth、変更されない provider ID、ユーザー別セッション、すべての API での所有者チェックが必要です。デバイスの鍵と本体でのペアリングは GitHub ログインと分離します。既存デバイスは現在の管理者を確認してから移行し、最初の OAuth 利用者に自動で渡してはいけません。秘密情報は Web ルートと Git の外に保存します。公開登録前に別アカウント間の権限分離を検証します。複数ワーカーには共通の状態管理と DB 移行も必要です。この文書だけで GitHub ログインが有効になることはありません。
