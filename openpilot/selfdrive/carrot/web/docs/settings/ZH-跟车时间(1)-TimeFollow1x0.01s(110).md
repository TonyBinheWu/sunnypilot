<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="TFollowGap1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟车时间(1): TimeFollow1x0.01s(110)

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN TFollowGap1 -->
<a id="TFollowGap1"></a>

## 跟车时间(1): TimeFollow1x0.01s(110)

`TFollowGap1`

巡航车距1级的基本跟车时间。50=0.50秒。应用速度TF倍率及驾驶、减速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap1 -->
<!-- CARROT:AUTO:SOURCE facts="75a34d280cac2c8471e07f68b5fff6467c8680c1d9fbcde0f0f45d7bd949ca16" semantic="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `110`
- **范围:** `40` ~ `300`
- **步长:** `5`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap1 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap1 -->
<!-- CARROT:REVIEW reviewed-for="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

巡航车距1级的基本跟车时间。增大则基本车距变长，减小则变短。应用速度TF倍率及驾驶、减速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

保存值50表示0.50秒。不同车距级别可设置相同基本TF和不同前车响应。路径上的横条及米数表示动态修正后的跟车目标距离。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap1 -->

<!-- CARROT:SETTING:END TFollowGap1 -->
