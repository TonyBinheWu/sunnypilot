<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 加速度設定 2: 40km/h(120)

**選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals2 -->
<a id="CruiseMaxVals2"></a>

## 加速度設定 2: 40km/h(120)

`CruiseMaxVals2`

40 km/h 到 60 km/h 的加速度

<!-- CARROT:AUTO:BEGIN CruiseMaxVals2 -->
<!-- CARROT:AUTO:SOURCE facts="2944b5818da8619711e3f15be9f5902ba638fd0657f77b05ee63baed958d1c9b" semantic="c060531fe2257a6fffdd9b0584198873e3bd3e85c69c0949ae84ab45a88bbabb" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `120`
- **範圍:** `1` ~ `250`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals2 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals2 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

從 40 km/h 到 60 km/h 的加速度。

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
<!-- CARROT:MANUAL:END CruiseMaxVals2 -->

<!-- CARROT:SETTING:END CruiseMaxVals2 -->
