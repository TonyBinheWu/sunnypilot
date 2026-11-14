<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="TESLA_FEATURES" param="TeslaAutoSpeedLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla 自動滾輪調速

**選單:** 駕駛控制 \> Tesla 專用 \> Tesla 功能

---

<!-- CARROT:SETTING:BEGIN TeslaAutoSpeedLimit -->
<a id="TeslaAutoSpeedLimit"></a>

## Tesla 自動滾輪調速

`TeslaAutoSpeedLimit`

預設關閉，變更後需完整重新啟動。受支援的 Tesla 須已偵測額外車輛 CAN 且啟用 alpha 縱向控制；巡航與 carrotpilot 啟用時，依原車 DAS 限速，以每次 1 km/h 或 1 mph 調整巡航設定速度。關閉時不設定自動滾輪傳送及相應 Panda 權限，保留手動滾輪。原先自動啟用的車輛也需開啟此選項。導航／Carrot 速度控制作用中暫停。手動滾輪會暫停自動調整；1 秒內向兩個相反方向滾動，或解除後重新啟用巡航可恢復。保留煞車、資料過期及無回饋保護；軟體測試不代表實車或道路驗收。

<!-- CARROT:AUTO:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:AUTO:SOURCE facts="28f50913a8cec686e3927e01dbbc8acf29faae4a265841c8951852ac9462bda3" semantic="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> Tesla 專用 \> Tesla 功能
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoSpeedLimit -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:REVIEW reviewed-for="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

受支援的 Tesla 須有額外車輛 CAN 及 alpha 縱向控制；巡航作用中，依原車 DAS 限速以顯示單位逐步調整設定速度。關閉時不設定自動滾輪傳送及相應 Panda 權限，保留手動滾輪及其他控制路徑。導航／Carrot 速度控制優先，並保留煞車、過期輸入及無確認回饋保護。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

在 Tesla 專用群組開啟後完整重啟。原先自動啟用的車輛現在也須明確開啟。手動滾輪會暫停自動調整；1秒內先向一方再向反方向滾動，或解除後重新啟用巡航可恢復。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 參考

僅跟隨原車限速，不會自動啟用巡航。軟體檢查不代表實車或道路驗收。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TeslaAutoSpeedLimit -->

<!-- CARROT:SETTING:END TeslaAutoSpeedLimit -->
