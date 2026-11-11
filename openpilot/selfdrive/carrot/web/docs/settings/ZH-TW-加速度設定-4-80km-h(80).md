<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 加速度設定 4: 80km/h(80)

**選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals4 -->
<a id="CruiseMaxVals4"></a>

## 加速度設定 4: 80km/h(80)

`CruiseMaxVals4`

80 km/h 到 110 km/h 的加速度

<!-- CARROT:AUTO:BEGIN CruiseMaxVals4 -->
<!-- CARROT:AUTO:SOURCE facts="f3adacf4c7cd2b71e967d76494c7eaed440b69a9e1df1830e9301bea94392c99" semantic="16e9dff4d42f6574aceb681dbdd9e8a5c2375b0f618309fb416550a7722a5e13" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `80`
- **範圍:** `1` ~ `250`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals4 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals4 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

從 80 km/h 到 110 km/h 的加速度。

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
<!-- CARROT:MANUAL:END CruiseMaxVals4 -->

<!-- CARROT:SETTING:END CruiseMaxVals4 -->
