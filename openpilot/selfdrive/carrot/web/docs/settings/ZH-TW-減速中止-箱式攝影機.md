<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SPEED_CAMERA" param="VehicleNaviDecelCancelBox" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 減速中止：箱式攝影機

**選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelBox -->
<a id="VehicleNaviDecelCancelBox"></a>

## 減速中止：箱式攝影機

`VehicleNaviDecelCancelBox`

減速中止請求開啟時，允許用巡航 + 鍵或輕踩油門中止箱式（移動攝影機箱，預告型別 2）攝影機的減速。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelBox -->
<!-- CARROT:AUTO:SOURCE facts="71884729f9fa7879f80306283eaf812de9a57e90f2b6348a16624b864247eb29" semantic="42f846ee76666e7420105b1833d0fa4ff8f300b9c3d5efc820cd0fdc3d3d1eef" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `1`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 速度與減速 \> 測速攝影機
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelBox -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelBox -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

取消減速總開關啟用時，啟用此項可用 + 或輕踩油門取消箱式測速照相減速；停用則不允許取消此類減速。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

若同時存在固定式、號誌或後方執法預告，仍會保留該執法項目的減速。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelBox -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelBox -->
