<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="TFollowGap4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟车时间(4): TimeFollow4x0.01s(160)

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN TFollowGap4 -->
<a id="TFollowGap4"></a>

## 跟车时间(4): TimeFollow4x0.01s(160)

`TFollowGap4`

巡航车距4级的基本跟车时间。50=0.50秒。应用速度TF倍率及驾驶、减速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap4 -->
<!-- CARROT:AUTO:SOURCE facts="20420d5fd460d47f9b4f818c993d8b0e81fa6a8e157b82b4ec73f57700e03c72" semantic="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `160`
- **范围:** `40` ~ `300`
- **步长:** `5`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap4 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap4 -->
<!-- CARROT:REVIEW reviewed-for="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

巡航车距4级的基本跟车时间。增大则基本车距变长，减小则变短。应用速度TF倍率及驾驶、减速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

保存值50表示0.50秒。不同车距级别可设置相同基本TF和不同前车响应。路径上的横条及米数表示动态修正后的跟车目标距离。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap4 -->

<!-- CARROT:SETTING:END TFollowGap4 -->
