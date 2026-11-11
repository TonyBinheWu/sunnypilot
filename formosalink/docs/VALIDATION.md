# 驗證紀錄 / Validation / 検証記録

## 2026-11-11 裝置資訊與停車設定（0.3.0）

- 兩分支各 68 項 Python 測試、4 項前端契約測試；包含原有配對／OAuth／監看回歸與新增設定測試。新增案例涵蓋簽章與重播、跨用戶 404、停車／本機授權／freshness、全設定 revision 衝突、型別與步進、離線逾時、一次性配送、回執遺失與重啟、撤銷及 v2→v3 備份後資料保留。
- 兩分支各 C3X／C4 原生 PC profile，各 11 項通過（共 44）：真實 UI frame、QR 三語解碼、停車限制、本機授權、原生 Params 寫入與回讀、原生 C3X／C4 控制項快取刷新不寫回或呼叫 callback。兩環境各自重新建置 libparams_c，保持分支原生差異。
- 瀏覽器以隔離測試帳號／裝置，在 390×844 手機尺寸驗證三語切換、深色語系選單、資訊／設定表單，確認「已送出」經真實簽章 HTTPS client → server → guarded provider → 回讀 → receipt，顯示「裝置已套用」且值更新。測試 provider 僅寫入記憶體 fixture，未對實車改值；頁面無水平溢出。截圖為測試裝置，不是正式實車資料。
- PowerShell 5.1 安裝腳本語法通過，保留 UTF-8 BOM；啟動成功條件更新為 offroad-settings 與 database_version 3。正式 IIS 執行中的後端在本次發布前仍為 schema 2；SMB 複製檔案無法替代主機執行更新指令。正式啟用結果須待主機更新後確認，勿以本機成功代替正式部署成功。
- 本批未改控制器、模型、CAN、safety 或既有行車設定預設值。PC profile 不是實體硬體模擬或實車駕駛驗收；行車狀態切換的硬即時性、實車不同能力目錄與資源用量仍需實機檢查。先前大模型場景限制仍見 SIMULATION_2026_11_09.md。


## 2026-11-10 介面與 QR 配對（0.2.1）

- 兩分支各 43 項後端測試、4 項前端測試通過。含 QR fragment 嚴格解析、期限、sessionStorage 往返／清除、偽造／重複欄位拒絕、簽章狀態查詢、防重放、QR 不被輪詢刷新，以及既有自架 origin 沿用。
- C3X/C4 × hkg-enhanced/ccnc-port：每組 8/8 原生檢查通過。新增三語實際繪圖截取後解碼 QR（共 12 張）、行車中阻擋、停用／關閉後忽略舊回應、撤銷關閉 agent、兩種原生設定入口建構。檔案路徑修正及測試副本分支設定來源修正後，完整四組重新通過。
- 瀏覽器本機測試：參考 sunnylink 深藍／紫藍介面，三語桌面與 390px 手機布局無水平溢出；無密碼或手動配對輸入。使用本機 mock OAuth provider 驗證「QR → 登入往返 → 自動確認畫面 → 配對成功」；同頁 hashchange 亦可接收 QR。
- 本批沒有修改車輛控制、安全、模型或 AGNOS；C3X/C4 是原生 PC profile 測試，不是實機／實車驗收。既有閉迴路模擬限制仍見下方歷史紀錄。
- 功能提交 2fa6f12（hkg-enhanced）、112b5e5（ccnc-port）的 Windows/Linux × Python 3.12/3.14 CI 全部成功：[HKG QR CI](https://github.com/TonyBinheWu/sunnypilot/actions/runs/42790750027)、[CCNC QR CI](https://github.com/TonyBinheWu/sunnypilot/actions/runs/42790761848)。
- IIS 新增 `qr-pairing` health 與簽章狀態 API；更新時保留原 GitHub 設定、資料庫及裝置。部署與重啟方式見 [QR_PAIRING.md](QR_PAIRING.md)。

English: Both branches pass 43 backend and 4 web tests. Each of four native branch/device profiles passes 8 checks, including actual rendered QR decoding in three languages. Browser QA verifies responsive layouts and QR/OAuth confirmation with a local mock provider. These are PC profile checks, not physical device or driving acceptance.

日本語：両ブランチでバックエンド 43 件、Web 4 件が成功しました。C3X/C4 の 4 組は各 8 件成功し、3 言語の実描画 QR を読み取れました。ブラウザーでモバイル表示とローカル mock OAuth の登録を確認しました。実機・実車の検証ではありません。

## 2026-11-10 GitHub 帳號及權限隔離（0.2）

- Python 3.14.10 本機後端套件：39 passed。包含真實本機 HTTP／WebSocket agent 回報、GitHub HTTP 交換契約（MockTransport）、OAuth state／PKCE／到期／重放／瀏覽器綁定、登出取消連結、禁止帳號接管、雙用戶裝置清單及撤銷隔離、禁止傳入 owner_id，以及 SQLite v1 既有 session／裝置金鑰備份遷移。
- Windows PowerShell 5.1 安全資料至 Python stdin 的端到端測試通過，Windows 密碼視窗控制項建構及取消清理測試通過（使用測試密鑰）；安裝器在停止服務前收集 OAuth 設定。IIS 已加入 no-cache 與前端資產版本號，避免新舊語言模組混用。
- 前端三語完整性與安全顯示測試：2 passed。Windows PowerShell 5.1 安裝腳本語法檢查通過。
- 兩分支各 C3X（tizi/BIG=1）與 C4（mici/BIG=0）：每組 4/4 原生 Linux 整合檢查通過，包含 UI 真實 frame、AGNOS manifest 與 agent 預設關閉。這是 PC profile 檢查，並非實機模擬器或實車驗證。這批沒有修改行車模組／agent 協定；先前閉迴路模擬的限制仍見 [模擬紀錄](SIMULATION_2026_11_09.md)，不能視為行車驗收通過。
- 正式 API 已確認 v2 schema 與 device-ownership 功能。原本配對的模擬裝置在升級後以相同金鑰送出一次簽章 HTTPS 回報，收到 200 / ack（sequence 10001），確認既有身分與配對仍有效。
- 正式 GitHub 授權與原管理者連結已確認：瀏覽器顯示 GitHub · TonyBinheWu，原部署驗證模擬裝置保留；簽章 HTTPS 回報 200 / ack（sequence 10002），畫面顯示 1 台連線中及預期模擬數值。用戶目前沒有第二個 GitHub 帳號，兩個真實帳號的外部隔離尚未驗證；後端跨帳號測試已通過。
- 功能提交 ea1e550（hkg-enhanced）、19ebde5（ccnc-port）的 Windows/Linux × Python 3.12/3.14 CI 全部成功：[HKG CI](https://github.com/TonyBinheWu/sunnypilot/actions/runs/42740648459)、[CCNC CI](https://github.com/TonyBinheWu/sunnypilot/actions/runs/42740831077)。

English: 39 backend tests and 2 frontend tests pass locally; GitHub requests are mocked except real local agent transport. Four native UI/profile checks pass for each branch/profile. No physical C3X/C4 or vehicle acceptance is claimed. Production GitHub authorization, explicit administrator linking, original-device retention and signed demo monitoring are verified. A second real GitHub account was unavailable; live two-account isolation remains unverified.

日本語：バックエンド 39 件・フロントエンド 2 件が成功し、両ブランチの C3X/C4 PC profile は各 4 件成功しました。実機・実車の検証ではありません。GitHub の本番認証・管理者連携・既存デバイスと模擬監視を確認しました。第 2 の実アカウントがないため、実アカウント間の確認は未実施です。

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


## 2026-11-11 正式 IIS 更新後驗證

使用者在 IIS 主機完成 setup-server.ps1 後，正式 HTTPS health 已回傳 qr-pairing、offroad-settings 與 database_version 3。瀏覽器既有 GitHub session 仍可登入 TonyBinheWu，原「部署驗證・模擬裝置」配對保留。使用相同裝置身分的 Ed25519 簽章回報與獨立 HTTPS 設定同步均成功。

在正式網站提交模擬裝置 QuietMode 變更，經伺服器配送、記憶體 fixture 套用與回讀、簽章 receipt 回傳後，網站顯示「裝置已套用」且勾選值更新。此測試只操作明確標示 DEMO 的既有模擬裝置，未呼叫原生 Params、未改實車設定。驗證後停止 agent，並以簽章同步關閉模擬裝置的遠端設定授權；資料過期後自動禁止編輯。實車仍需更新對應分支並由本機明確開啟停車遠端設定後另行驗證。

功能提交的 Windows/Linux × Python 3.12/3.14 CI 兩分支共 8 組全部通過：
- hkg-enhanced 52b7310：https://github.com/TonyBinheWu/sunnypilot/actions/runs/42927015209
- ccnc-port 86380f3：https://github.com/TonyBinheWu/sunnypilot/actions/runs/42927025343


## 2026-11-11 分類後台（0.3.1）

設定視窗改為淺色完整後台，依參考畫面加入左側分類、線框圖示、跨分類搜尋、裝置切換、狀態提示、手機抽屜及三語選單。使用隔離 localhost 帳號／兩台模擬裝置驗證分類切換、搜尋、重新整理保留分類、上一頁、切換裝置清除舊內容，以及設定儲存經既有簽章通道顯示裝置已套用。390×844 手機檢查無水平溢出；包含減少動態效果模式下側欄確實隱藏與正常展開。模型／地圖明確標記未開放，不宣稱已支援模型下載或切換。原生 agent、後端協定與寫入檢查未修改；前端新增分類／搜尋／網址契約測試，共 5 項。發布前仍重跑兩分支各 68 項 Python 與 C3X／C4 各 11 項原生檢查。


## 2026-11-11 健康總覽、暗色主題與導航（0.4.0）

- 新增原生健康 adapter 與所有者隔離的健康摘要：預設零值／缺失／過期不偽裝即時資料；body SOC 支援有效 0%，其他未解碼車型顯示未提供。區分內建 GPU 與 Chestnut eGPU 的不存在、安裝但無溫度及未知狀態；原生溫度清單上限 32。
- 三語淺色／暗色／跟隨系統、偏好重載記憶、多裝置首頁、手機 390×844、SOC／eGPU 兩種安裝狀態及無水平溢出已用清楚標示 DEMO 的本機 fixture 驗證。模擬電量與溫度僅供畫面驗證，未宣稱是真車感測值。
- 瀏覽器貼入完整地圖 URL，帶入座標後傳送 DEMO 目的地，經真實 HTTPS 簽章 agent → API → 記憶體 provider → 回讀 → receipt，顯示裝置已套用；未呼叫外部地圖網址或寫實車。本機原生 profile 另測實際 Params JSON NavDestination 寫入回讀。
- 兩分支各 77 項 Python、7 項前端測試；C3X／C4 各 12 項原生 profile（共 48）。涵蓋 SOC 0／未提供、eGPU 缺失與過期、目的地嚴格型別／座標範圍／額外欄位拒絕、停車與本機導航啟用檢查、監看模式不外傳原生目的地，以及跨用戶健康資訊隔離。
- 無行車／CAN 解碼／原生 navd 修改；目的地接收不代表路線成功，實際 SOC 支援、硬體溫度／eGPU 及實車導航仍需對應硬體驗收。正式 IIS 需更新執行中後端至 device-health／navigation-destination，原資料庫維持 schema 3，既有帳號與配對保留。


0.4.0 正式更新後：使用者執行 IIS 更新，正式 health 已確認 device-health 與 navigation-destination，schema 3、原 GitHub session／裝置配對保留。以既有 DEMO 身分送簽章健康摘要，正式首頁顯示測試溫度、SOC 未提供與 eGPU 未安裝；主題淺色／暗色切換成功。在正式導航頁輸入 DEMO 名稱與公開測試座標，經記憶體 provider 寫入回讀及簽章 receipt 後顯示裝置已套用。未啟動實車導航，未向路線供應商查詢。測試後停止回報、關閉模擬遠端授權並使健康讀值失效；實體裝置、SOC、eGPU 與路線計算驗收仍須實機。


## 2026-11-11 自動 SOC 辨識與統一入口（0.4.1）

- hkg-enhanced／ccnc-port 各 88 項 Python、7 項前端測試通過。兩分支的 C3X／C4 原生 UI／Params／DBC profile 各 14 項，共 56 項通過。以各分支鎖定的 opendbc 檢查全部 79 個 Hyundai／Kia／Genesis 平台定義：60 個傳統 CAN 具有經核對的 BAT11；19 個 CAN-FD 不啟用 SOC 解碼。以原生 CANPacker 產生封包驗證位元解碼與實際 CarParams 自動選擇，不需使用者挑選車型。
- BAT11 是 12V 輔助電池；高壓 SOC 尚未支援。本版沒有啟用 Kona 未確認候選訊號，也沒有主動診斷輪詢。測試涵蓋零值、非法值、長度、bus、重複、過期、平台切換與 DBC 變更停用；不代表所有實車都會發送 BAT11。
- 原生行車解析器、控制器、safety 與 opendbc gitlink 維持原狀；獨立 FormosaLink subscriber 僅被動讀取 CAN。實車 CAN、上車資源負載與硬體驗收仍待完成。此矩陣是原生 PC profile 與合成封包檢查，未宣稱完成真車或閉環行車模擬驗收。
- 公開入口改成與內頁相同的簡潔配色，登入且有配對裝置時直接開啟「所有裝置」。localhost DEMO 驗證公開入口、登入路由、淺色／暗色、390×844 單欄與明確區隔高壓／12V SOC。合成 72% 為測試資料。
- 無後端 API／資料庫變更；原 0.4.0 IIS 不需重啟或重設帳密／OAuth。裝置需更新對應分支。完整訊號證據與限制見 HYUNDAI_SOC.md。


## 2026-11-11 設定控制項、逐項同步與衝突（0.5.0）

兩分支各 89 項 Python 與 18 項 Node 測試通過。新增的回讀不一致測試確認不能標記 applied；前端涵蓋依 command ID 逐項確認、草稿保留、外部同值不冒充成功、session／schema 衝突、明確 rebase 後再儲存、遺失回應禁止自動重試、跨帳號清除及導航 JSON 比較。兩分支 C3X／C4 原生 profile 各 14 項，共 56 項通過；未修改行車程式或裝置協定。

本機兩個瀏覽器分頁使用真實簽章 ManagementClient、HTTP API 與記憶體 Params fixture：一邊保留數值／開關草稿，另一邊修改相同數值並取得回讀成功；第一邊顯示裝置值與草稿的衝突、保留未衝突草稿，保留我的修改後仍需再次儲存。導航亦依自己的命令 receipt 顯示結果。所有測試裝置／座標明確標示 DEMO，未修改實車。

本版只部署靜態前端與文件／測試，現有 IIS 0.4.0 後端及 schema 3 相容，無須主機重啟。草稿和逐項操作追蹤只保留於目前分頁，重新整理會清除；沒有新增自動離線命令配送。實車驗收仍獨立進行。

補充瀏覽器驗證：繁體中文／英文／日文切換保留相同衝突與草稿；手機 390×844 下頁面 clientWidth 與 scrollWidth 均為 375（扣除捲軸），無水平溢出。確認採用裝置值會清除該項草稿並顯示最新值，其他項目草稿不受影響；淺色與暗色畫面已保存。
