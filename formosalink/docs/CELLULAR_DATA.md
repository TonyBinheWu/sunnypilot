# SIM 行動數據開關（0.6.1）

## 繁體中文

- C3X：設定 → 網路 → 進階 → **SIM 行動數據**。
- C4：設定 → 網路 → **SIM 行動數據**。
- 停車時可開關。預設開啟，升級時缺少此參數也沿用原本連線行為；選擇會保留到重開機後。SIM 留在機內，不需拆機插拔。
- 關閉的是行動數據 PPP 連線，不是飛航模式或 SIM 拔除；不改 Wi-Fi、APN、漫遊、SIM/eSIM 設定，也不新增數據機 RF／GNSS 電源控制。SIM 仍可保持註冊，這不等同 RF 完全靜默。
- 原生 modem 下一次迴圈會停止 PPP、清理原生 PPP 路由並掛斷數據埠；PPP 程序或 ppp0 還存在時不回報停用完成，後續重試。停用期間不自動重撥、不反覆切換 DTR。重新啟用後回到原生初始化／註冊／撥號流程，不保證在無訊號或資費受限時成功連線。
- FormosaLink 裝置資訊顯示「SIM 行動數據設定」與「SIM 數據連線狀態」，區分要求開關與實際狀態。數據機回報超過 10 秒即顯示未知／過期，不把尚未斷線誤報為已關閉。
- 此開關限本機，網頁不能寫入 `GsmDataEnabled`。SIM 是唯一連線時，關閉後網站會離線；在裝置重新開啟即可。連上 Wi-Fi 時仍可透過 Wi-Fi 監看。

### 更新與驗證

兩分支均新增預設為 true 的 `GsmDataEnabled`（PERSISTENT／BACKUP），僅修改原生數據機資料連線狀態機與網路設定，不改車型、控制器、safety、模型或導航。需要更新裝置分支並重新啟動載入新版 modem。原生開關不需 IIS 後端遷移，新的網頁狀態標籤為靜態更新。

主機測試涵蓋所有狀態下關閉、預設／升級保持連線、停止後不重撥、重新啟用、停止失敗與 PPP 未清乾淨時不宣稱成功、停車及型別檢查、三語與過期狀態。原生 C3X／C4 profile 另驗證 UI 能啟動、實際 Params 預設與持久化、兩種網路 UI 回呼及禁止行駛中修改。這些是 PC 原生 profile 與注入的 PPP 測試；SIM 實體數據機、網路恢復時間、Wi-Fi 與 GNSS 同時運作仍須實機驗收。

本批兩分支各 120 項 Python、20 項前端測試通過，C3X／C4 每分支各 17 項原生檢查，共 68 項通過。原生 UI 首輪發現初始化語系取用錯誤，已修正並重跑全部四個 profile，UI 可持續輸出畫面。實體數據機驗收仍待進行。

### 維護

本功能原生共用檔案為 `openpilot/common/hardware/comma/modem.py`、`openpilot/system/ui/lib/cellular_data.py`、兩種 network UI 及 params_keys.h 的單一參數。兩分支以相同修改同步；不要整份覆寫分支專屬 params_keys.h。GsmDataEnabled 刻意排除在遠端設定 catalog 之外。

設計參考：NetworkManager 的 [radio／rfkill 說明](https://networkmanager.dev/docs/rfkill/) 將 WWAN radio 開關列為 RF 控制；本版沒有採用該方式，而是在目前分支原生 PPP 狀態機停止數據連線。

## English

C3X: Settings → Network → Advanced → SIM mobile data. C4: Settings → Network → SIM mobile data. Change while parked. The default remains on, and the preference survives reboot. No physical SIM removal is needed.

Off stops native PPP data, cleans its routes and hangs up the data port. It does not delete a SIM/eSIM, change APN/Wi-Fi or add RF/GNSS power control. It is not airplane mode; cellular registration may remain. A remaining PPP process/interface prevents a false disabled acknowledgement. On resumes the existing native initialization and dial path.

The web dashboard reports requested and fresh effective states separately; the switch is local only to preserve recovery when cellular is the sole connection. Update the matching device branch and restart. No IIS backend migration is needed for this feature. PC profiles and mocked PPP tests do not replace physical modem, Wi-Fi and GNSS acceptance.

## 日本語

C3X は設定 → ネットワーク → 詳細 → SIM モバイルデータ、C4 は設定 → ネットワーク → SIM モバイルデータで切り替えます。停車中のみ操作でき、初期値はオン、再起動後も選択を保持します。SIM を取り外す必要はありません。

オフは原生 PPP データ接続とその経路を停止し、データ用ポートを切断します。SIM/eSIM の削除、APN／Wi-Fi の変更、RF／GNSS 電源制御は行いません。機内モードではなく、網への登録は残る場合があります。PPP が残っていれば停止完了と表示しません。オンにすると既存の初期化と接続処理へ戻ります。

ウェブは設定値と新鮮な実際の状態を区別して表示します。回復できるようスイッチは本体のみです。該当ブランチを更新して再起動してください。この機能のための IIS 移行は不要ですが、実機の通信・Wi-Fi・GNSS は別途検証が必要です。
