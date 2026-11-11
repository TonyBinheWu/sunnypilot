# 設定操作與逐項同步（0.5.0）

## 繁體中文

本版參考 [sunnylink-frontend](https://github.com/sunnypilot/sunnylink-frontend/tree/26795b7766413369f03c105fda6cd4f1e53eae1f) 的 schema 控制項、逐項狀態及衝突提示，使用 FormosaLink 自己的實作與既有簽章通道。沒有引入官方 Logto／Athena 相依服務，也沒有改動裝置行車功能。

### 操作

- 依裝置實際回報的型別、範圍、間距、選項及啟用條件產生開關、數值加減／輸入、分段選項或下拉選單。不可用的設定會停用並顯示提示。沒有任意 Params 寫入入口。
- 修改後顯示「尚未儲存」，每一項需要按儲存。其他項目的草稿會保留，切換分類、搜尋、語言或裝置後仍可繼續編輯。草稿只存於目前分頁記憶體，不存 localStorage；重新整理、登出、帳號變更或取消配對會清除。導航目的地的草稿也遵守此規則。
- 各設定分別顯示正在送出、等待接收、等待裝置回讀確認、已套用或失敗。HTTP 200、快照剛好相同或其他設定的成功，都不能使這個設定顯示已套用。只有相符 command ID 的裝置回讀 receipt 才能確認。
- 裝置值、停車 session 或設定 schema 改變時，未送出的修改會進入衝突狀態。顯示裝置目前值與我的修改；「採用裝置值」會捨棄草稿，「保留我的修改」只更新比較基準，仍需再次按儲存。設定已移除或停用時無法強行送出。
- 若伺服器／裝置在送出時發現 revision 不符，也會保留草稿並要求確認。網路回應遺失時顯示結果不明，不自動重送；至少等待 60 秒、取得新鮮狀態且沒有待處理命令後，才轉成需要人工核對的狀態。可再次收到原命令 receipt 時仍採用其結果。
- 同一裝置維持一次一項待處理命令，沿用 20 秒命令期限、所有權隔離、原生停車狀態、本機允許、session／revision 檢查及寫入回讀。其他控制項仍可編輯草稿，不會自動合併送出或在重新連線後自動套用。

### 部署與驗證

本批只有前端及測試變更，沿用現有 0.4.0 後端 API 和 schema 3。執行 `tools/deploy/publish_formosalink_iis.ps1` 發布至既有 IIS 即可，無須重啟 Python、重設 OAuth、重新配對或更新車端才能使用這些介面改進。車端可用控制項仍取決於已安裝分支與本機授權。

```powershell
python -m pytest formosalink/tests -q
node --test formosalink/tests/web.test.mjs
```

前端測試包含草稿保留、跨裝置／帳號清除、同值不冒充成功、command ID 對應、衝突處理、遺失回應及導航 JSON 格式。Python 新增寫入後回讀不一致必須拒絕的測試。原生 C3X／C4 profile 另檢查既有裝置寫入保護；不等同實車行車驗收。

## English

Controls follow each device's typed catalog: switches, numeric steppers, segmented choices and dropdowns. Every edit needs an explicit Save. Per-setting state distinguishes unsaved, sending, queued, waiting for readback, confirmed and failed. Only the matching command's device receipt confirms application; HTTP acceptance or a matching snapshot never does.

Drafts are kept per device in this tab's memory and cleared by reload, sign-out, account changes or unpairing. A device value, session or schema change requires review. Use device value discards the edit; Keep my edit rebases it but still requires Save. Lost responses are not retried automatically. After 60 seconds and a fresh, non-pending device state, the user must review before retrying. Existing parked-state, ownership, local opt-in, revision and readback checks remain unchanged.

Deploy the static package to the existing IIS site. No backend restart, migration, OAuth configuration or new pairing is required for this UI update. Device capabilities still depend on its installed version.

## 日本語

本体が通知する型・値域・刻み幅・選択肢・利用条件から、スイッチ、数値操作、分割選択、ドロップダウンを生成します。変更は各項目の保存で送信します。未保存・送信中・受信待ち・再読込確認待ち・適用済み・失敗を区別し、対応する command ID の本体 receipt のみで適用済みと判定します。

変更はこのタブのメモリーでデバイス別に保持し、再読込・ログアウト・アカウント変更・登録解除で消去します。本体値・session・schema が変わった場合は、自分の変更と本体値を比較できます。本体の値を採用すると変更を破棄し、自分の変更を保持しても再度保存が必要です。応答が失われても自動再送しません。60 秒後に新鮮な状態と待機命令がないことを確認してから、再確認を求めます。

既存 IIS へ静的ファイルを配布すれば利用できます。Python の再起動、データ移行、OAuth の再設定、再登録は不要です。本体の停車・許可・revision・書込み後の再読込確認は維持します。
