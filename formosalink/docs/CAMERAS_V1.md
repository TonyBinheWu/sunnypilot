# FormosaLink 0.7.0：背景服務與雙鏡頭 / Background cameras / バックグラウンドカメラ

## 繁體中文

- C3X 使用原生大型設定列表，C4 使用原生大型滑動卡片。裝置端只保留配對及停車遠端設定許可，不再顯示監看開關。背景 agent 預設啟用，仍須獨立 QR/GitHub 配對；既有配對與金鑰保留。
- SIM 連線狀態另外讀取核心 PPP 介面的 UP/RUNNING 旗標和 IPv4，使用獨立檢查時間，避免慢速 AT 查詢的回報過期造成假斷線。真正失去介面／IP 會立即反映。這仍是數據連線狀態，不是網際網路可達性測試；實體訊號或 APN 問題不會被顯示濾波掩蓋。
- 網頁「影音」可選超廣角或車內鏡頭。兩者使用 camerad 的 wide-road／cabin IPC，唯讀取得 NV12，透過裝置已附的 FFmpeg 編成 JPEG。保留完整長寬比，最大 640×360，約每兩秒一張；兩個網頁可分別選不同鏡頭。此版沒有音訊或完整行車疊圖。
- 只有裝置所有者登入後，才能建立 15 秒觀看請求；觀看時自動續期。裝置在背景輪詢簽章通道，只針對有請求的鏡頭傳送。關閉網頁後最多約 15 秒停止傳送；伺服器只保留最多三秒的新鮮影格，不建立錄影歷史。按網頁「錄影」才會在瀏覽器本機保留短片。
- 熄火時，新的相機程序條件僅在這個短效請求有效且背景服務啟用時才允許 camerad 執行；不寫入 IsDriverViewEnabled／IsLiveStreaming，不改行車狀態、模型、控制器、IR 或 CAN。請求失效會恢復原本程序條件。裝置仍須有電且連線；不提供遠端開機。實車負載、夜間車內畫面與行動網路恢復仍須驗收。

## 部署

1. 更新對應 hkg-enhanced／ccnc-port 並重新啟動裝置。原本明確關閉監看的舊值會按本次需求升級為開啟；遠端設定的本機許可不會自動開啟。
2. 發布至 IIS 後，在 IIS 主機的系統管理員 PowerShell 執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython
```

保留 SQLite、原管理者、OAuth 與配對，不需再次輸入密碼。啟動腳本只有確認 `/api/v1/health` 出現 `native-camera-preview-v1` 後才顯示成功。IIS 的私有執行中服務不會因共享資料夾更新而自行載入新版。

3. 手機登入後開啟裝置的「影音」，選鏡頭並開始觀看。未更新後端會明確要求升級；無新鮮影像時不保留舊畫面。電腦驗證使用合成 NV12／DEMO 影像，不代表已驗證實車畫面。

## English

The C3X page uses native large settings rows; C4 uses native swipe cards. Monitoring is background-enabled without a device toggle; QR/GitHub ownership and separate parked-setting consent remain required. Kernel PPP flags/address provide fresh data-link feedback independently of slow AT queries. Real disconnects remain visible; Internet access is not inferred.

The web viewer selects ultra-wide or cabin IPC. Native NV12 is read without modifying shared buffers and encoded by bundled FFmpeg at up to 640×360, preserving aspect ratio, approximately one frame every two seconds. There is no audio or full driving overlay. Only an authenticated owner can create/renew a 15-second camera lease. The signed device channel fetches demand; inactive viewers cease uploads within roughly 15 seconds. Server frames expire after three seconds; recordings are browser-local and explicit. Offroad camerad is permitted only during a valid lease, without writing driver-view/live-stream flags or changing driving/model/controller/CAN/IR behavior.

Update and reboot devices, and run the IIS host setup command above to load the new API. Existing credentials, OAuth, pairings and SQLite remain intact. Health must advertise `native-camera-preview-v1`. IPC, encoding and browser acceptance use synthetic frames; real camera, device load and cellular recovery acceptance remain pending.

## 日本語

C3X は原生の大きな設定行、C4 は原生のスワイプカードを使用します。本体の監視スイッチを削除し、登録後は既定でバックグラウンド動作します。QR/GitHub の所有権登録と停車中の遠隔設定許可は分離したままです。PPP の旗標と IPv4 を独立に取得し、遅い AT 応答による誤った切断表示を防ぎます。実際の切断は表示し、インターネット到達性とは区別します。

ウェブで超広角／車内カメラを選択します。原生 IPC の NV12 を読み取り専用で取得し、付属 FFmpeg で最大 640×360、約２秒に１枚の JPEG に変換します。音声・詳細な走行オーバーレイは含みません。所有者だけが 15 秒の視聴要求を作成・更新でき、視聴終了後は約15秒以内に送信を停止します。画像はサーバーのメモリで３秒以内に失効し、録画は明示的な操作時のみブラウザー内に保存します。停車中の camerad は有効な視聴要求中のみ追加実行し、走行・モデル・制御・CAN・IR の設定は変更しません。

デバイス更新と再起動、IIS ホストで上記コマンドを実行してください。既存の認証・登録・データベースを保持し、ヘルス応答の `native-camera-preview-v1` を確認します。検証画像は合成画像で、実車カメラ・負荷・通信回復は別途確認が必要です。
