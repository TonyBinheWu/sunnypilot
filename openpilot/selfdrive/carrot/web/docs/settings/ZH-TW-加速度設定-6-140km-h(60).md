<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals6" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 加速度設定 6: 140km/h(60)

**選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals6 -->
<a id="CruiseMaxVals6"></a>

## 加速度設定 6: 140km/h(60)

`CruiseMaxVals6`

140 km/h 以上的加速度

<!-- CARROT:AUTO:BEGIN CruiseMaxVals6 -->
<!-- CARROT:AUTO:SOURCE facts="8f68d7d8ceb498188a3acf844d41b57ca328b8983af22b7a52f7a43644c65752" semantic="2ef3b0ff9376edca155222806f33b84fd52d4ac09bcf4b0887d38f856e800145" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `60`
- **範圍:** `1` ~ `250`
- **步長:** `5`
- **選單:** 駕駛控制 \> 巡航與車距 \> 加速特性 \> 速度加速表
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals6 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals6 -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

140 km/h 以上的加速度。

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
<!-- CARROT:MANUAL:END CruiseMaxVals6 -->

<!-- CARROT:SETTING:END CruiseMaxVals6 -->
