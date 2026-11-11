<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals0" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 加速度設定 0: 0km/h(160)

**選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals0 -->
<a id="CruiseMaxVals0"></a>

## 加速度設定 0: 0km/h(160)

`CruiseMaxVals0`

0 km/h 到 10 km/h 的加速度

<!-- CARROT:AUTO:BEGIN CruiseMaxVals0 -->
<!-- CARROT:AUTO:SOURCE facts="e7d762660c82443fa0d0978cd9a4065893f142f47a962bda9013c56461d4b739" semantic="10e4085bba3a9694e8a989ade4077d532afaa5245b9d72df8bcdfd397cb650f0" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `160`
- **範圍:** `1` ~ `250`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals0 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals0 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

從 0 km/h 到 10 km/h 的加速度。

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
<!-- CARROT:MANUAL:END CruiseMaxVals0 -->

<!-- CARROT:SETTING:END CruiseMaxVals0 -->
