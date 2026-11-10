# 驗證紀錄 / Validation / 検証記録

## 2026-11-10 GitHub 帳號及權限隔離（0.2）

- Python 3.14.10 本機後端套件：39 passed。包含真實本機 HTTP／WebSocket agent 回報、GitHub HTTP 交換契約（MockTransport）、OAuth state／PKCE／到期／重放／瀏覽器綁定、登出取消連結、禁止帳號接管、雙用戶裝置清單及撤銷隔離、禁止傳入 owner_id，以及 SQLite v1 既有 session／裝置金鑰備份遷移。
- Windows PowerShell 5.1 安全資料至 Python stdin 的端到端測試通過，Windows 密碼視窗控制項建構及取消清理測試通過（使用測試密鑰）；安裝器在停止服務前收集 OAuth 設定。IIS 已加入 no-cache 與前端資產版本號，避免新舊語言模組混用。
- 前端三語完整性與安全顯示測試：2 passed。Windows PowerShell 5.1 安裝腳本語法檢查通過。
- 兩分支各 C3X（tizi/BIG=1）與 C4（mici/BIG=0）：每組 4/4 原生 Linux 整合檢查通過，包含 UI 真實 frame、AGNOS manifest 與 agent 預設關閉。這是 PC profile 檢查，並非實機模擬器或實車驗證。這批沒有修改行車模組／agent 協定；先前閉迴路模擬的限制仍見 [模擬紀錄](SIMULATION_2026_11_09.md)，不能視為行車驗收通過。
- 正式 API 已確認 v2 schema 與 device-ownership 功能。原本配對的模擬裝置在升級後以相同金鑰送出一次簽章 HTTPS 回報，收到 200 / ack（sequence 10001），確認既有身分與配對仍有效。
- 正式 GitHub 授權、原管理者連結，以及兩個真實不同 GitHub 帳號的外部隔離驗證，須等待 OAuth App 與 IIS 私有後端設定完成；本機 mock 測試不等於已通過正式 GitHub 登入。

English: 39 backend tests and 2 frontend tests pass locally; GitHub requests are mocked except real local agent transport. Four native UI/profile checks pass for each branch/profile. No physical C3X/C4 or vehicle acceptance is claimed. Live GitHub authorization and two-real-account validation remain pending host OAuth setup.

日本語：バックエンド 39 件・フロントエンド 2 件が成功し、両ブランチの C3X/C4 PC profile は各 4 件成功しました。実機・実車の検証ではありません。GitHub の本番認証と実アカウント 2 件での確認はホスト設定後に行います。

## 2026-11-10 正式部署完成驗證

- 正式網址：`https://formosapilot.dinglu-t.com`。
- 外部健康檢查：200，包含 `device-pairing` 與 `signed-https-telemetry` 功能旗標，確認新版已載入。
- 使用者親自在正式網站登入並確認測試裝置配對；未向開發端提供管理者密碼。
- 已配對的獨立測試身分傳送簽章 HTTPS 模擬資料：200，收到對應 sequence 的 ack。
- 未登入讀取 `/api/v1/devices`：401。
- 正式瀏覽器驗證：1 台已配對、1 台連線中；顯示「部署驗證・模擬裝置」、CPU 46°C、GPU 43°C、記憶體 31%、可用儲存 72%。這些是明確標記的模擬資料，沒有連接真實車輛。
- Cloudflare／IIS 的 WebSocket 握手仍不相容；目前使用已驗證的簽章 HTTPS 備援，不停用 TLS 憑證驗證。既有簽章、nonce 防重放、資料白名單與撤銷規則皆保留。
- 本次短時測試回報結束後，測試裝置會依 20 秒有效期顯示離線；真實裝置需在本機完成自己的配對並啟用 agent。
- 部署腳本已建立開機排程與私有程式／資料目錄；本次未重啟整台 IIS 主機測試開機恢復。

Production validation completed on 2026-11-10: health and signed telemetry returned 200; unauthenticated device reads returned 401. The owner logged in and paired the labelled demo device personally. The live dashboard showed one paired/online device and simulated metrics. Transport is signed HTTPS fallback; WebSocket proxy interoperability remains unresolved. No real vehicle or physical C3X/C4 was connected, and server reboot recovery was not exercised.

2026-11-10 に本番サイトで正常性・署名付き HTTPS 送信の 200、未ログイン API の 401、所有者によるログインとペアリング、1 台の接続中表示を確認しました。数値は明示された模擬データです。WebSocket の代理接続問題は残るため署名付き HTTPS を使用し、TLS 検証は無効化していません。実車や実機、サーバー再起動の検証ではありません。

## 初回実装の履歴 / Initial implementation record

Date: 2026-11-09 (Asia/Taipei). First batch, FormosaLink 0.1.0 / protocol v1.

This is the initial implementation record. Later service fixes have 29 passing backend tests on isolated Python 3.14.10 plus two passing UI tests. For the actual pre-push native UI/telemetry matrix, model failures and baseline comparison, see [SIMULATION_2026_11_09.md](SIMULATION_2026_11_09.md). Deployment state below reflects the initial publication, not the subsequent service startup.

| Check | hkg-enhanced | ccnc-port |
| --- | --- | --- |
| Python host suite, including real HTTP/WebSocket client | 25 passed | 25 passed |
| UI language completeness and rendering safety | 2 passed | 2 passed |
| Architecture module inventory | 15 definitions valid | 15 definitions valid |
| Shared companion source comparison | Identical | Identical |

Host: Windows, Python 3.13.9. CI is configured for Python 3.12 on Windows/Linux but has not been run remotely. Three dependency deprecation warnings originate from uvicorn's default websockets legacy transport; they do not indicate failing assertions.

Browser QA: 390 × 844 mobile viewport; Traditional Chinese, English and Japanese; owner login, live labelled demo telemetry, pairing form, language switching and desktop layout. Only explicit test data was used, never real vehicle data. The preview server and demo agent were stopped after screenshots were saved under the workspace's ignored `build/` directory.

Deployment: files copied to `\\192.168.20.145\htdocs\FormosaPilot`, with SHA-256 verification. HTTPS homepage returned 200; backend health endpoint returned 502; a direct request for protected App_Data Python source returned 404. Backend initialization, owner password, Windows process startup and end-to-end IIS WebSocket forwarding remain to be completed on the server. No production credentials are generated or copied by the deployment script.

尚未完成 C3X／C4 原生建置、實機採樣、車上負載與雲端斷線行車驗證。本次不修改車型、控制器、safety、模型或 AGNOS。兩分支的修改尚未提交或推送。

C3X/C4 native builds, physical-device telemetry, runtime resource use and cloud-offline driving verification remain outstanding. Vehicle controllers, safety, models and AGNOS are outside this change. Changes in both branches remain uncommitted and unpushed.

C3X／C4 のビルド、実機の状態取得、負荷、クラウド切断時の運転支援動作は未検証です。車両制御、safety、モデル、AGNOS は変更していません。両ブランチともコミット・プッシュは行っていません。
