<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleSpeedCameraDistanceTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車輛測速攝影機虛擬距離時間（6.0秒）

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraDistanceTime -->
<a id="VehicleSpeedCameraDistanceTime"></a>

## 車輛測速攝影機虛擬距離時間（6.0秒）

`VehicleSpeedCameraDistanceTime`

僅在外部導航未連線時應用。外部導航連線期間，即使沒有當前引導專案也不使用原車導航。 當車輛僅傳送測速攝影機執法速度而沒有距離時，建立虛擬減速距離。儲存值以0.1秒為單位：60表示6.0秒，62表示6.2秒。虛擬距離（米）= 執法速度（km/h）× 設定時間（秒），因此在50 km/h時，62會生成310米。設定值越小，虛擬距離越短，因此可能會更早或更強地開始減速。更改後的值會在行駛中約1秒內生效。 支援的CAN-FD車輛在沒有與當前警告匹配的近處距離時也適用。新警告或限速變化會重新開始計算；距離耗盡後，只要警告仍有效就保持限速，不會反覆延長虛擬距離。

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:AUTO:SOURCE facts="2b29d999e785b80c0eaf886ec87579e4172107e9c785fcdc7a2d89ae7a3860f0" semantic="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `60`
- **範圍:** `10` ~ `200`
- **步長:** `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:REVIEW reviewed-for="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" reviewed-at="2026-09-13T09:14:59.940344+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

外部導航連線期間僅使用外部導航，即使沒有當前引導專案也不使用原車導航。確認斷開連線或接收超時後，按各項設定恢復使用原車導航。

當車輛只提供執法速度而不提供距離時計算虛擬距離。增大數值會延長虛擬距離，減小數值會縮短距離，可能更早或更強地減速。
支援的CAN-FD車輛在沒有與當前警告匹配的近處距離時也使用此設定。新警告或限速變化會重新開始計算，並隨行駛距離減少。距離耗盡後，只要警告仍有效就保持限速，不會反覆延長虛擬距離。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

同時檢查外部導航連線狀態以及顯示的事件型別和剩餘距離。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:SETTING:END VehicleSpeedCameraDistanceTime -->
