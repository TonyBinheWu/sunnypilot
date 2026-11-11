# 裝置健康、主題與導航（0.4.0）

## 繁體中文

側欄底部與主畫面可切換「自動 → 淺色 → 暗色」，選擇儲存在此瀏覽器；自動模式跟隨系統。首頁「所有裝置」顯示登入者每台已配對裝置的車型／VIN、車輛 SOC、C3X／C4 本體 CPU／內建 GPU／最高溫，以及 eGPU 溫度。「所有溫度感測器」展開後可看記憶體、DSP、電源晶片、數據機與 C4 進氣、排氣、GNSS、底部 SoC 晶片等可用讀值。SoC 晶片溫度與車輛電池 SOC 分開標示。

資料來源為有效且新鮮的原生 deviceState、carState、chestnutGpuState。溫度缺失、非有限、預設 0 或過期不視為有效讀值。eGPU 偵測目前支援原生 Chestnut：由 deviceState.chestnutPresent 確認是否安裝，再由有效 chestnutGpuState 取顯卡與顯存溫度。未安裝、已安裝但沒有溫度、無法確認三種狀態分開；未支援的第三方 eGPU 不宣稱已可靠辨識。

SOC 需原車型解碼支援。已審查的目前 opendbc 只有 body 解碼器寫入 carState.fuelGauge，其他車型不能將預設 0 當作電量。支援來源可正確呈現 0%；其他顯示「車輛未提供 SOC」，不從 12V 電壓推估高壓電池電量。若要支援 Hyundai／Kia 等車型的真實 SOC，需另行新增並驗證對應 CAN 解碼；本批未改動行車／CAN 解碼器。健康資料超過 10 秒未更新即停止顯示為即時讀值，各用戶資料仍由後端隔離。

### 導航操作

1. 更新對應裝置分支，停車後允許 FormosaLink 遠端設定，並在裝置啟用原生 NavigationEnabled。C4 目前可於原生開發者設定找到 navigation (alpha)；其他硬體的導航顯示能力依原分支而定。
2. 網頁開啟「導航」，貼上 `緯度,經度` 或包含座標的完整地圖網址，再按「帶入座標」。支援 Google Maps 的 @座標／q／query、Apple Maps 的 ll，以及 OpenStreetMap 的 #map。短網址不會由服務代為展開，請先自行開啟再複製座標。
3. 填寫名稱、核對座標，按「傳送至裝置導航」。只有停車、狀態新鮮、裝置允許遠端設定及原生導航啟用時可送出。沿用 20 秒逾時、一次性配送、session／revision 檢查、原生寫入與回讀確認。
4. 裝置收到嚴格限定的 latitude、longitude、place_name，寫入原生 JSON NavDestination。網站顯示「裝置已套用」代表目的地已回讀，**不表示 GPS 定位、路線計算或導航畫面已驗收**。路線由裝置原生 navd 處理，仍需要其 GPS／Mapbox 或既有路線服務；本批未提供自架地址搜尋、路線引擎或修改原生 navd。

導航目的地是位置資料，傳送至自己的 FormosaLink 伺服器並由所有者查看。只有本機允許遠端設定時才同步既有原生目的地；僅監看不會上傳目的地。車輛即時 GPS、行程軌跡與影像仍不傳送。地圖連結只在瀏覽器解析座標，不請求連結網站、不保存分享連結。

### IIS 與裝置更新

先發布套件，再於 IIS 主機的系統管理員 PowerShell 執行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "\\192.168.20.145\htdocs\FormosaPilot\App_Data\setup-server.ps1" -InstallPython
```

保留管理者、OAuth 與配對，無須重新輸入密碼／Secret，資料庫維持 schema 3。health 需同時包含 device-health 與 navigation-destination。之後更新對應裝置分支，才會有真實新增感測器與目的地同步；舊 agent 保持相容監看。雲端或網路中斷不改動原生行車預設行為。

## English

Choose Auto, Light or Dark; the browser retains the preference. All devices shows owner-scoped vehicle identity, supported battery SOC, device temperatures and native Chestnut eGPU GPU/VRAM temperatures. Expand all sensors for available CPU, internal GPU, memory, DSP, PMIC, modem and C4 intake/exhaust/GNSS/bottom-SoC readings. Missing/stale/default-zero thermal values are unknown. A fresh native presence flag distinguishes absent eGPU from installed-but-unavailable and unknown. Other eGPU implementations require their own adapter.

Current audited car decoders only publish battery fuelGauge for comma body. Other brands show SOC unavailable, never fabricated zero; 0% remains valid for a supported decoder. No CAN/control changes are included.

Navigation accepts coordinates or full coordinate-bearing map links, parsed locally without fetching them. Enable native navigation and local parked remote settings first. A strict destination uses latitude, longitude and place_name, passing existing ownership, parked-state, revision/session and expiry checks before writing native JSON NavDestination. Receipt confirmation means destination readback, not validated route calculation. Device GPS and its existing Mapbox/comma routing configuration remain required; no self-hosted geocoder/router is included. Monitoring-only mode never exports native destinations. Live GPS, tracks and camera feeds remain excluded.

Run the IIS command above locally, then update the matching device branch. Credentials/pairings remain and database schema stays 3. Health advertises device-health and navigation-destination. Physical vehicle and routing acceptance remain separate checks.

## 日本語

自動・ライト・ダークを切り替え、ブラウザーに保存します。全デバイスで自分の車両情報、対応する SOC、本体温度、Chestnut eGPU／VRAM 温度を確認できます。全センサーを展開すると対応する CPU、内蔵 GPU、メモリ、DSP、電源 IC、モデム、C4 の吸排気／GNSS／底面 SoC を表示します。欠損・期限切れ・既定値の温度は不明とし、eGPU の未装着と温度未取得を区別します。

現在の車両デコーダーで電池 fuelGauge を公開するのは body のみです。その他の車種は SOC 未提供と表示し、0% を推測しません。CAN／運転制御は変更しません。

ナビでは座標または座標を含む完全な地図 URL を貼り付け、本体のナビへ目的地を送信できます。短縮 URL は自動展開せず、リンクを外部へ取得しません。本体でナビと停車中の遠隔設定を許可し、状態・期限・revision を確認後、厳密な目的地を原生 JSON NavDestination に書き込み再読込します。「適用済み」は目的地の受信確認で、経路計算の成功を意味しません。本体の GPS と既存の経路サービスが必要です。自架の住所検索／経路エンジンは今回の対象外です。監視のみでは既存の目的地を送信せず、現在位置や映像も送信しません。

IIS ホストで上記コマンドを実行後、対応ブランチの本体も更新してください。認証情報と登録を維持し、データベースは schema 3 のままです。実車での受入検証は別途必要です。
