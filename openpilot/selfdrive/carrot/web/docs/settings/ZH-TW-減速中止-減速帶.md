<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviDecelCancelBump" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速中止：減速帶

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelBump -->
<a id="VehicleNaviDecelCancelBump"></a>

## 減速中止：減速帶

`VehicleNaviDecelCancelBump`

減速中止請求開啟時，允許用巡航 + 鍵或輕踩油門中止原車導航減速帶減速。僅在減速帶目標速度（由 AutoNaviSpeedBumpSpeed、AutoNaviSpeedBumpTime、AutoNaviSpeedDecelRate 計算）低於設定速度、即實際減速時才使用該輸入。中止只適用於最近的一個減速帶。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:AUTO:SOURCE facts="37e553b28e93ebc8fda6edc67805a5e7b8f19ed4280e9ce8e72261855537cbf8" semantic="ab15a94879c1067db343091913a6b8ee055f955c0564f0b44795d843826bedfd" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `1`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelBump -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

取消減速總開關啟用時，啟用此項可用 + 或輕踩油門取消最近減速丘的減速；停用則不允許取消此類減速。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

只有計算出的減速丘目標低於設定速度，且正實際降低目標速度時，才會使用此輸入。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelBump -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelBump -->
