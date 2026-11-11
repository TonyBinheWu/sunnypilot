<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviDecelCancelMobileZone" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速中止：移動測速區間

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelMobileZone -->
<a id="VehicleNaviDecelCancelMobileZone"></a>

## 減速中止：移動測速區間

`VehicleNaviDecelCancelMobileZone`

減速中止請求開啟時，允許用巡航 + 鍵或輕踩油門中止移動測速區間（導航藍色圓圈）的減速。導航減速模式（AutoNaviSpeedCtrlMode）為 3 時移動區間才會減速，模式 2 及以下不生效。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:AUTO:SOURCE facts="a56ff62c80a172e9771aa66c0eabfe6945c4b8a12d7a84510dfda6bd73b25038" semantic="570b00e282ceb2973c52e7d7121aea5fd059e453aac9b714b972da032891c62e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `1`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

取消減速總開關啟用時，啟用此項可用 + 或輕踩油門取消移動式測速區域減速；停用則不允許取消此類減速。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

移動式測速區域減速本身只在導航減速模式 3 運作。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelMobileZone -->
