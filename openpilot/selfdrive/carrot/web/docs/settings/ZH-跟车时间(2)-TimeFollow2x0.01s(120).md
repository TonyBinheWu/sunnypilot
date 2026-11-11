<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="TFollowGap2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟车时间(2): TimeFollow2x0.01s(120)

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN TFollowGap2 -->
<a id="TFollowGap2"></a>

## 跟车时间(2): TimeFollow2x0.01s(120)

`TFollowGap2`

巡航车距2级的基本跟车时间。50=0.50秒。应用速度TF倍率及驾驶、减速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap2 -->
<!-- CARROT:AUTO:SOURCE facts="289a2b838accf8db02ec859fb752c0eb13f41eaa48bf405af1fdefde1ebf5b13" semantic="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `120`
- **范围:** `40` ~ `300`
- **步长:** `5`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap2 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap2 -->
<!-- CARROT:REVIEW reviewed-for="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

巡航车距2级的基本跟车时间。增大则基本车距变长，减小则变短。应用速度TF倍率及驾驶、减速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

保存值50表示0.50秒。不同车距级别可设置相同基本TF和不同前车响应。路径上的横条及米数表示动态修正后的跟车目标距离。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap2 -->

<!-- CARROT:SETTING:END TFollowGap2 -->
