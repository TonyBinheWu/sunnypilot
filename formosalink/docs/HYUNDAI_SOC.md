# Hyundai / Kia SOC audit — 0.4.1

## 繁體中文

FormosaLink 沿用原生 CarParams 的車型辨識，自動選擇 CAN／CAN-FD 與動力類型，不要求使用者選解碼器。這不代表每台車都有可取得的高壓電池 SOC。

| 項目 | 已確認的範圍 |
| --- | --- |
| 兩分支的原生 Hyundai／Kia／Genesis 平台 | 各 79 個平台定義已測試辨識路徑 |
| 傳統 CAN | 60 個平台的目前 DBC 包含相同 BAT11 定義；收到有效封包時可讀取 **12V 輔助電池 SOC** |
| CAN-FD | 19 個平台；目前沒有啟用任何未驗證的 SOC 解碼 |
| HEV／PHEV／EV 高壓電池 SOC | 尚未支援；不以 12V SOC 或電壓替代，不顯示假造的 0% |

79 是平台定義數，不是已完成道路驗證的車型／年份數。平台可共用多個商品車型，且 DBC 有定義不表示每台車都裝有電池感測器或會送出該訊息。沒有訊息時顯示等待／未提供。

已核對兩分支各自鎖定的 opendbc：hkg-enhanced `1c51731784729da5ebaf24b3c34106bd27aaf94b`，ccnc-port `23330cb5ab3ff9668421603dac22a4e98060b67c`。`hyundai_can.dbc` 中 BAT11 為 0x549、8 bytes，BAT_SOC 位元 16、長度 8、倍率 1%；BAT_SNSR_V 位元 24、長度 14、倍率 0.001、偏移 6 V，範圍 6–18 V。這是輔助電池訊號。啟動時核對實際 DBC 欄位；上游定義改變即停止使用此解碼。

參考來源：[commaai 原始 DBC](https://github.com/commaai/opendbc/blob/master/opendbc/dbc/generator/hyundai/hyundai_can.dbc)。另查閱 [Kona EV 社群 DBC](https://github.com/projectgus/kona-ev-dbc/blob/main/pcan.dbc)：其 0x542 SocDisp 註解仍標為 unconfirmed，不能據此套用所有 Hyundai／Kia，更不能套用 CAN-FD。診斷 PID 查詢與被動 CAN 監聽不同，本版沒有主動 OBD／UDS 輪詢。

### 實作與限制

- 獨立 daemon 接收原生 `can` 訊息，僅接受傳統 CAN bus 0、正確 ID／長度、合法電壓及 0–100% SOC。至少兩個不同時間且新鮮的封包才顯示；2 秒沒有新資料即失效。拒絕全零／全 FF、重複、過期或未來封包。
- 此 observer 不發送 CAN、不寫 Params，不改 carState、行車解析器、控制器、safety、車型辨識或原生必要訊息檢查。裝置仍須開啟既有 FormosaLink 監看；關閉／斷網不阻擋原生行車程序。
- 網頁將「車輛 SOC 電量」與「12V 輔助電池 SOC／電壓」分開；保留其他原生已支援 SOC 來源。繁體中文、英文、日文均有標籤。
- 高壓 SOC 後續需逐平台比對被動封包、儀表 SOC、位元定義、無效值與 CAN bus，並取得包含 0%、充放電與斷訊的測試資料。未完成前維持未支援。主機與合成 CAN 測試不代表實車驗收。

### 更新

網站靜態檔與伺服器套件發布至既有 IIS，無後端 API／資料庫遷移，已執行 0.4.0 的主機不需重啟或重設 OAuth。裝置更新對應分支後才會執行新的 observer。舊裝置持續使用原本監看。

## English

Automatic selection follows native CarParams, flags and the pinned DBC. Both branches test 79 Hyundai/Kia/Genesis platform definitions: 60 classic CAN definitions contain BAT11, while 19 CAN-FD definitions remain SOC unsupported. BAT11 is **12V auxiliary battery SOC**, not HEV/PHEV/EV traction SOC. A definition does not prove every vehicle sends it. No signal means unavailable; zero is accepted only from valid fresh frames. Traction SOC remains unverified and unsupported across this adapter.

The independent subscriber checks the exact DBC metadata and accepts only bus 0 / 0x549 / 8-byte frames, requires two fresh distinct frames, and expires readings after two seconds. It never transmits CAN or writes Params, and does not change driving parsers or controllers. No active diagnostic polling is included. Native profile and synthetic CAN tests are not physical-vehicle acceptance. Update the matching device branch; the existing 0.4.0 IIS backend requires no restart or data migration.

## 日本語

原生 CarParams と DBC から車種・CAN／CAN-FD・動力方式を自動判別します。両ブランチで各 79 プラットフォーム定義を検査しました。従来 CAN の 60 定義にある BAT11 は **12V 補機バッテリー SOC** です。高電圧駆動用バッテリーの SOC ではありません。CAN-FD の 19 定義と駆動用 SOC は未対応で、推測値を表示しません。実車がメッセージを送らない場合も取得不可になります。

独立した受信処理で DBC 定義、バス、ID、長さ、値域、鮮度を確認し、2 件の有効フレームを必要とします。2 秒で期限切れになります。CAN 送信・Params 書込み・運転制御の変更はありません。合成 CAN と PC 上の原生プロファイル検査は実車検証の代わりにはなりません。デバイスを該当ブランチに更新してください。0.4.0 の IIS バックエンドの再起動や移行は不要です。
