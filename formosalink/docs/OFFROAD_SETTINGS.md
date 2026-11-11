# 裝置資訊與停車設定 / Device settings / 停車中の設定（0.3.0）

## 繁體中文

配對後，在裝置卡片選擇「資訊與設定」。資訊包含硬體、序號、系統／軟體版本、分支、提交、車型／VIN（有資料時）、運作時間、網路、溫度、記憶體、空間、功耗、風扇與亮度。不傳送密碼、金鑰、位置、攝影機或任意 Params。

1. 更新對應的 `hkg-enhanced` 或 `ccnc-port` 裝置版本。既有獨立身分與配對沿用。
2. 停車後，在裝置 **設定 → 裝置 → FormosaLink** 開啟「停車遠端設定」。預設關閉；配對不會自動授權修改。關閉監看會一併關閉遠端設定。
3. 手機登入，開啟「資訊與設定」，搜尋設定並逐項儲存。網頁顯示「裝置已套用」才表示裝置完成寫入與回讀。送出、已接收、拒絕、逾時均分別顯示。
4. 本機修改會在下次同步反映於網站。遠端寫入會更新原生控制項快取，不觸發重複寫入或控制項 callback。需要重新啟動／下次行車週期才生效的原生設定，仍遵循原生生命週期。

設定目錄直接取自各分支 `sunnylink/settings_ui.json` 及動態扭力選項，沿用原生型別、範圍、步進、車型／能力及相依條件。未支援或條件不符的設定停用。設定標題、選項與操作介面提供繁中／英文／日文。模型選擇、更新動作、重啟／移除、SSH／ADB、服務啟動、攝影機／麥克風上傳同意等不經此通道開放；不是 sunnylink 所有雲端功能的完整複製。

裝置每 5 秒使用獨立簽章 HTTPS 通道同步資訊、值與回執；目錄僅在變更／伺服器需要時傳送。編輯需伺服器資料 10 秒內、停車且本機允許。裝置在每次寫入前再次確認 manager `IsOffroad`、2 秒內有效的 `deviceState` 與 `pandaStates`、未 started、無 ignition、本機授權、狀態 session、完整設定 revision 及期限。每次僅一個參數，一次僅一筆待完成操作，20 秒逾時；失聯不會累積稍後執行的操作。原生 Params 沒有跨服務的行車狀態交易鎖；檢查緊接寫入，仍須實機驗證切換與時序，不宣稱硬即時保證。

### 目前 IIS 更新

網站與後端套件可由 `tools/deploy/publish_formosalink_iis.ps1` 發布至既有網站。僅複製檔案不會更新已啟動的私有後端；在 **192.168.20.145 本機系統管理員 PowerShell** 執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython
```

無須重新輸入 GitHub Secret 或管理者密碼。程式保留設定與配對，第一次從 SQLite v2 升級時先建立私有 `formosalink.sqlite3.before-v3.sqlite3` 備份，再新增管理快照與操作表。成功條件：`/api/v1/health` 同時回傳 `offroad-settings` 與 `database_version:3`。只有 SMB 存取時，部署端無法代替主機重新啟動排程。

回復須先在主機停止 FormosaLink 排程並確認服務結束，另存目前資料庫，還原 `.before-v3.sqlite3` 與相符的 0.2.x 程式後啟動。不要執行中覆寫 SQLite；回復會移除升級後的設定記錄。重複備份檔存在時停止遷移，須人工確認。未更新的舊裝置仍可回報監看資料，但不會提供新設定通道。

## English

Open **Info and settings** on a paired device. Update the matching device branch, then explicitly enable **Parked settings** on its local FormosaLink screen. Pairing alone grants no write permission. Choose a supported setting, save it, and wait for **Applied by device**. Native settings that require a restart or a new drive retain that behavior. Local changes return to the web; native control caches refresh after remote writes without callbacks or duplicate writes.

The catalog uses each branch’s native sunnylink definitions, capabilities, types, options and ranges. This channel excludes privileged service actions, updates/reboots, shell/SSH/ADB, model selection, and camera/audio consent. It is not full sunnylink feature parity. Device information uses an explicit allowlist and excludes credentials, location and camera streams.

Signed HTTPS sync runs every five seconds independently of telemetry WebSockets. The server requires a snapshot received within ten seconds and owner-scoped authentication. Commands expire after twenty seconds, deliver at most once, and never form an offline backlog. The device rechecks fresh valid hardware/manager parked state, local permission, session and all-settings revision immediately before a single typed write; readback precedes acknowledgement. A persisted receipt journal prevents replay after a crash or lost acknowledgement. Native Params has no cross-service ignition transaction lock; physical transition timing remains a required hardware test.

Run the PowerShell command above locally on the existing IIS host after publishing. Existing password, GitHub credentials and pairings remain. Schema v2 is backed up to `.before-v3.sqlite3` before migration. Health must advertise `offroad-settings` and database version 3. SMB publication cannot restart the private host service. Old agents remain telemetry-compatible. For rollback, stop the host service, archive the current database, restore the v2 backup and matching old runtime, then restart; never replace a live SQLite file.

## 日本語

登録済みデバイスの **情報と設定** を開きます。対応ブランチへ本体を更新し、本体の FormosaLink 画面で **停車中の遠隔設定** を有効にしてください。登録だけでは書き込みを許可しません。設定を保存し、**本体に適用済み** の表示を待ちます。再起動や次の走行を必要とする設定は、従来の動作を維持します。本体での変更も Web に反映され、遠隔変更後はネイティブ UI のキャッシュを再読込します。

項目・型・範囲・車種条件は各ブランチの sunnylink 定義を使用します。更新・再起動・シェル・SSH／ADB・モデル選択・カメラ／音声送信への同意は対象外です。sunnylink の全機能の複製ではありません。認証情報、位置、映像は送信しません。

署名付き HTTPS で 5 秒ごとに同期します。Web 側は所有者と 10 秒以内の状態を確認します。本体は書き込み直前に 2 秒以内の有効な停車状態、イグニッション、本体の許可、session、revision、期限を再確認します。1 回につき 1 項目、20 秒で期限切れとなり、オフラインの操作は蓄積しません。書込後の再読込で適用を確認し、永続化した受領記録で再実行を防ぎます。Params は走行状態との共通トランザクションを持たないため、状態遷移の実機検証は別途必要です。

公開後、IIS ホスト本体の管理者 PowerShell で上記コマンドを実行してください。既存のパスワード、GitHub 設定、登録情報を維持し、v2 のバックアップ後に v3 へ移行します。health の `offroad-settings` と `database_version:3` を確認してください。SMB でのファイル配置だけではサービスは更新されません。復元時は必ずサービスを停止し、現データを保管したうえで v2 バックアップと対応する旧コードを戻してください。


## 0.3.1 分類後台 / Categorized workspace / 分類画面

「資訊與設定」現在開啟獨立淺色後台：左側分類導覽、上方跨分類搜尋（Ctrl／Cmd K）、自己的裝置切換、連線狀態與離線提示。網址保留裝置與分類，可重新整理或使用上一頁／下一頁。手機使用抽屜選單，底部語系選單可選繁中／英文／日文。模型與地圖頁面明確顯示目前未開放，不提供尚未支援的操作；原有停車檢查與簽章協定不變。

Info and settings now opens a light full-page workspace with category navigation, cross-category search (Ctrl/Cmd K), owner-scoped device switching, connection state and stale-data notices. Device/category hash routes survive reload and browser history. Mobile navigation uses a drawer. Models/maps explicitly show their unavailable status. Existing offroad write guards are unchanged.

情報と設定は、分類ナビゲーション・全分類検索・所有デバイスの切替・接続状態を備えた明るい専用画面になりました。URL の装置／分類を再読込や履歴でも保持します。スマートフォンはドロワー式メニューです。モデル／地図は未対応と明示し、停車時の書込制限は従来どおりです。

今回の変更はフロントエンドのみです。IIS へ公開後、ブラウザーを再読込してください。後端の再起動や OAuth 設定の再入力は不要です。／本次僅更新前端，發布後重新整理即可，無須重跑後端安裝或輸入 OAuth Secret。／Frontend-only update: reload after publishing; no backend restart or OAuth reconfiguration is needed.
