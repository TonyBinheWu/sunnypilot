<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviDecelCancelUnknown" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速中止：未識別型別的測速攝影機 \[實驗\]

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelUnknown -->
<a id="VehicleNaviDecelCancelUnknown"></a>

## 減速中止：未識別型別的測速攝影機 \[實驗\]

`VehicleNaviDecelCancelUnknown`

減速中止請求開啟時，允許用巡航 + 鍵或輕踩油門中止原車導航測速警告中未收到或無法解析攝影機型別預告（CAN 未接收/未處理）的警告的減速（實驗功能）。由於型別未知，可能包含無預告的闖紅燈或測速攝影機，因此預設關閉，即使開啟上級也需單獨開啟。30km/h 及以下的警告（兒童·老人保護區等）和區間測速中不適用。中止後若匹配到闖紅燈、後向或固定預告，則遵循該型別的規則。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:AUTO:SOURCE facts="e68f6210d133b26a52184a07522c8fda9b160ba2bb468b0382da64ee21c4f786" semantic="bc790dfd91a22232bbc47f0077d136baa937beae69d660870e3b370ffa0052a7" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelUnknown -->
