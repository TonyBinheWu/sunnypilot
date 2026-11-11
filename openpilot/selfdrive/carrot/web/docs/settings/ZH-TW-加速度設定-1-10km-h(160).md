<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 加速度設定 1: 10km/h(160)

**選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals1 -->
<a id="CruiseMaxVals1"></a>

## 加速度設定 1: 10km/h(160)

`CruiseMaxVals1`

10 km/h 到 40 km/h 的加速度

<!-- CARROT:AUTO:BEGIN CruiseMaxVals1 -->
<!-- CARROT:AUTO:SOURCE facts="1dc3b15d666d69bfcc9b5baa29149ca26d48c31c70c84e78689fca0a92b9b3cf" semantic="049a2f4d59b41e828fa48bb99c19bfa5060440ba1382f09e912dd397a5c1816d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `160`
- **範圍:** `1` ~ `250`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals1 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals1 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

從 10 km/h 到 40 km/h 的加速度。

- **調高：** 允許此速度範圍使用較大的最大加速度。
- **調低：** 讓此速度範圍內的加速較溫和。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在適用速度範圍內逐步調整，確認加速至目標速度的表現及乘坐舒適度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

[相關英文操作指南](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseMaxVals1 -->

<!-- CARROT:SETTING:END CruiseMaxVals1 -->
