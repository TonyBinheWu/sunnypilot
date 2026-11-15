# FormosaPilot 0.9.0 instrument display / 儀表顯示 / メーター表示

## 繁體中文

第一階段參考 [Carrot carrot-wip](https://github.com/ajouatom/openpilot/tree/bc8eb4c2e1aac3023c99f3914e657ed9638beab7)，以獨立、預設關閉的儀表顯示功能整合，保留兩分支既有轉向、煞車、駕駛監控與接線選擇。

適用條件：Hyundai／Kia CAN-FD、相機側 SCC、非 LKA-steering 拓樸，且指紋階段在相機 bus 實際收到長度 32 bytes 的 `0x161` 和 `0x162`。不符合條件即不啟用，不能由車型名稱推定相容。

更新完整分支（包含 opendbc 與 Panda 子模組）後，在停車狀態開啟「車輛 → Hyundai → FormosaPilot 儀表顯示（實驗）」，再重新啟動。FormosaLink 的車輛設定也提供相同開關；須已有設定權限、裝置回報支援且停車才能修改。「已套用」代表參數已由裝置讀回，儀表模式須重啟才會生效。關閉後重啟恢復原有儀表處理路徑。

已整合：

- `0x161` 車道顏色、LFA 圖示、方向箭頭；只有原本已使用 openpilot 縱向控制時才更新速度／車距顯示。
- `0x162` 已知方框物件轉為車輛樣式；必須存在有效的原廠距離，隱藏物件及其他類型維持原樣。
- Panda 依原廠接收節奏轉送 `0x161`、`0x162`、`0x1E0`、`0x1EA`、`0x200`。後兩者未確認的欄位保持原樣，不增加訊息頻率。
- 每個 ID 僅保留最新有效主機資料；150 ms 逾時回到原廠內容。保留原廠 counter、物件座標、車道幾何、故障、聲音及未知位元，重算 checksum。
- 同步支援所選 Panda 的 bus offset；轉向／煞車封包不進入儀表快取。

本階段不包含 ADAS 改線控制路徑、車道變換控制或原廠沒有提供的物件／曲率資料。不能承諾所有 HDA2／ccNC 車型都可顯示完整畫面。未做實車儀表、道路及實際韌體燒錄驗證；程式測試和 ARM 建構不等於實車驗證。不要因為儀表圖案推定車輛具備新的駕駛能力。

主程式與 Panda 新介面必須一起更新；Panda 來源為 [FormosaPilot fork](https://github.com/TonyBinheWu/formosapilot-panda)，兩分支各自固定 opendbc commit，避免安全參數互相覆蓋。原作者授權與來源註記保留。

驗證方式：opendbc 的 `test_formosa_cluster`、`test_hyundai_cluster`、既有 Hyundai 安全測試、CAN parser/checksum 測試；FormosaLink `test_cluster_settings`；原生 `settings_ui_check` 在 C3X／C4 各跑一次；Panda H7 以兩份 opendbc 安全規則分別建構。涵蓋預設關閉、能力檢查、未知位元保留、CRC、逾時、counter wrap、relay fault 與既有控制路徑。

IIS 不負責車輛 CAN 控制。網頁沿用裝置上傳的設定目錄與逐項回讀確認；部署不會變更帳號、OAuth、配對或資料庫。裝置必須更新後才會提供此開關。

### 2026-11-11 驗證紀錄 / Validation / 検証

| 項目 / Suite | hkg-enhanced | ccnc-port |
| --- | --- | --- |
| Hyundai safety + CAN + cluster unittest | 5,758 run, 476 skipped, 0 failures | 6,202 run, 511 skipped, 0 failures |
| FormosaLink Python | 172 passed | 172 passed |
| Web Node | 21 passed | 21 passed |
| C3X native UI | 33 passed | 33 passed |
| C4 native UI | 33 passed | 33 passed |
| Panda H7 firmware + bootstub ARM build (`-Werror`) | passed | passed |

Host tests and native UI profiles are simulated checks, not physical vehicle validation. 韌體建構使用 debug 簽章，未向實機燒錄；實機由更新程序依固定來源建構。Panda: `5e0eb6e6210f2d5b734bec5e1c4073bb8b691096`; opendbc HKG: `4ece3bb`; CCNC: `2a565d3`。

## English

This first integration adds an optional OEM cluster overlay inspired by the pinned Carrot revision above. It is off by default and requires a restart. Existing steering, braking, driver monitoring and harness selection remain in place.

Eligibility requires Hyundai/Kia camera-SCC CAN-FD without LKA steering, with actual 32-byte `0x161` and `0x162` reception on the camera bus during fingerprinting. Vehicle names alone do not prove compatibility. Enable in Vehicle → Hyundai while parked, then restart. Remote writes also require existing settings permission and device readback; a saved setting is distinct from the active mode after restart.

`0x161` overlays lane/icon/arrow fields; speed and distance display fields change only with existing openpilot longitudinal control. `0x162` converts known boxes with real OEM distances to vehicle glyphs. Panda forwards five cluster IDs at OEM reception cadence, keeping counters, geometry, faults, sounds and unknown bits. `0x1EA`/`0x200` are unchanged. Each latest-only host cache expires at 150 ms; the original packet then passes through. Steering/braking commands are never cached. The selected Panda bus offset is respected.

This does not add the rewired ADAS control topology or new driving abilities, and cannot supply geometry absent from OEM traffic. Physical cluster behavior, flashing and road performance remain unverified. Both main code and the pinned Panda/opendbc dependencies must be updated together. Tests cover CRC, forwarding, protected bits, expiry, counter wrap, relay faults, existing controls and C3X/C4 native settings; both H7 firmware configurations are built. IIS continues using the device-owned catalog and readback protocol without changing accounts or pairings.

## 日本語

上記の Carrot リビジョンを参考に、純正メーター表示を補助する独立した機能を追加します。初期値はオフで、変更後は再起動が必要です。既存の操舵、制動、ドライバー監視、ハーネス設定を維持します。

対象は Hyundai／Kia のカメラ側 SCC CAN-FD で、LKA 操舵ではなく、識別時にカメラ bus で 32 bytes の `0x161` と `0x162` を実際に受信した構成です。車種名だけでは対応と判断しません。停車中に「車両 → Hyundai」のメーター表示を有効にして再起動します。遠隔変更には設定権限と装置の読戻し確認が必要です。保存完了と再起動後の有効化は異なります。

`0x161` の車線色、LFA アイコン、矢印を更新します。速度／車間表示の変更は既存の openpilot 縦制御使用時のみです。`0x162` は純正距離が有効な既知の四角形を車両表示へ変換します。Panda は純正受信に合わせて 5 種の ID を転送し、カウンター、位置、車線形状、故障、警告音、未知ビットを保持します。`0x1EA`／`0x200` は変更しません。最新データのみを保持し、150 ms で期限切れとなり純正内容へ戻ります。操舵／制動メッセージはキャッシュせず、選択された Panda の bus offset を使用します。

ADAS 配線変更用の制御経路や新しい運転機能は追加しません。純正データにない物体や形状は作成しません。実車表示、実機書込み、走行性能は未検証です。主プログラムと固定された Panda／opendbc を同時に更新してください。CRC、転送、保護ビット、期限、カウンター周回、relay fault、既存制御、C3X／C4 設定をテストし、両構成の H7 ファームウェアをビルドします。IIS のアカウント、OAuth、ペアリング、データベースは維持します。
