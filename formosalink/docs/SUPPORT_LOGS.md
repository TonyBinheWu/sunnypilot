# 管理者診斷台與行車紀錄分享

FormosaLink 0.9.0 新增裝置卡片的「診斷分享與行車紀錄」，以及管理者帳號的
「管理者診斷台」。帳號必須是既有 `local-admin`，或已明確連結到該管理者的
GitHub 身分。一般 GitHub 用戶只可查看、授權或刪除自己裝置的資料。

## 使用者操作

1. 更新車機與 IIS 後端，登入 FormosaLink 並完成裝置配對。
2. 裝置卡片 →「診斷分享與行車紀錄」→「開啟診斷分享」。確認後才會送出文字日誌，
   提供管理者協助抓錯誤；預設關閉。每個開機週期先傳一份，之後每 15 分鐘檢查變更，
   停車後上傳。停用分享會阻止後續診斷上傳，不自動刪除先前已傳的資料。
3. 完整行車紀錄須另外按「同意上傳最近完成行程」，每次確認僅授權一個任務，
   有效 24 小時。車機停車時選擇最近已完成的行程，傳送所有可取得的 `rlog.zst`／
   `rlog.bz2` 分段；包含位置、路線及行車狀態，不含攝影機影片。
4. 「刪除全部並停用分享」會刪除本裝置雲端檔案、取消未完成任務及停用診斷分享。
   撤銷配對後仍可從原帳號查看、刪除已傳紀錄，車機無法再上傳。

文字日誌來源：可取得的安裝器錯誤／日誌、AGNOS 更新、首次啟動失敗與 tmux 文字
輸出。每個來源只取末端 8 KiB，標示未找到的來源；遮蔽常見憑證、網址、IP、位置欄位
與長十六進位字串。這是文字規則，不能保證移除所有個人或環境資訊。
不收集 Params 目錄、私鑰、配對檔、Cookie、Wi-Fi 密碼或任意檔案。

安裝器未留下的日誌、配對以前沒有上傳的資料，無法還原。下載安裝檔的 HTTP 請求
不等於已安裝或成功開機。新功能不會讓管理者自動取得所有未配對或未同意使用者的資料。
目前不把安裝下載服務的平台日誌匯入 FormosaLink，也不宣稱涵蓋整個安裝流程。

## 管理者操作與限制

管理者診斷台可依裝置 UUID、檔名或類型搜尋最近紀錄，顯示裝置名稱、檔案大小與
到期時間。最多顯示 200 筆（查詢範圍最近 2,000 筆），可下載已通過 SHA-256 的完整
檔案。顯示檔案完成與行程任務狀態；部分分段成功不代表整趟行程完整。
無資料只代表尚未收到，不能推論車機沒有錯誤。

每個 rlog 上限 64 MiB，一個行程最多 128 分段／512 MiB，超限會回報而不默默省略
較大檔案。每裝置雲端預留容量上限 1 GiB，全站 10 GiB；達上限時拒絕新增上傳，
不會悄悄刪除 30 天內資料。若行程上傳失敗，已成功分段仍可下載，需由使用者重新
明確提交任務。中斷的檔案不公開下載；目前不支援跨程序重啟接續。

兩類檔案預設均保留 **30 天**，從開始上傳的時間計算，讀取時排除過期檔案並清理。
服務每小時清理一次，未完成檔案最多留一天；服務停機期間不會執行清理，重啟即清。
正式資料放在既有資料目錄的 `support/`，不放在 IIS 網站內。30 天清理不涵蓋系統管理者
另行製作的外部備份。

## 部署與驗證

更新車機 `carrot-wip` 並重啟。IIS 檔案用既有
`tools/deploy/publish_formosalink_iis.ps1` 發布，然後在 **IIS 主機本機**以系統管理員
PowerShell 執行網站的 `App_Data/setup-server.ps1`，沿用原有帳號、OAuth 與配對。
必須同時更新 Python 後端及網站；只更新靜態頁會遇到 API 404。
健康端點的 `support-logs-v1` 表示新後端功能已載入。

裝置以既有 Ed25519 身分簽署每個 32 KiB 區塊，檢查配對、來源、同意、到期、nonce、
容量、位移與最終 SHA-256。上傳佇列獨立於控制程序，雲端失敗不阻擋行車。
需要現場驗證 C4/C3X 日誌來源、耗時及 IIS 代理；主機測試不能代替實機驗收。

## English

Diagnostics sharing is off by default and owner-controlled. Available installation/startup/error
text tails are uploaded while parked, with common credential fields redacted. Each latest completed
drive rlog upload requires separate owner consent and includes location, but no video. Both expire
after 30 days. The administrator can search/download reports across consenting devices; ordinary
accounts retain strict owner isolation. Delete-all cancels jobs and disables sharing. Missing logs
and unpaired/pre-install stages cannot be reconstructed. Limits and partial-job states are explicit.

## 日本語

診断共有は既定で無効です。所有者の同意後、取得可能なインストール・起動・エラーの
テキスト末尾を停車中に送信します。走行 rlog は毎回別途同意が必要で、位置情報を含み、
映像は含みません。保存期間はいずれも 30 日です。管理者のみ共有された各デバイスの
記録を検索・ダウンロードできます。削除操作は待機中の処理と共有も停止します。
記録されていないインストール段階は復元できません。
