<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_GAP" param="TFollowGap3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 跟车时间(3): TimeFollow3x0.01s(140)

**菜单:** 驾驶控制 \> 巡航与车距 \> 车距

---

<!-- CARROT:SETTING:BEGIN TFollowGap3 -->
<a id="TFollowGap3"></a>

## 跟车时间(3): TimeFollow3x0.01s(140)

`TFollowGap3`

巡航车距3级的基本跟车时间。50=0.50秒。应用速度TF倍率及驾驶、减速修正。

<!-- CARROT:AUTO:BEGIN TFollowGap3 -->
<!-- CARROT:AUTO:SOURCE facts="1c07e3d0a58071a198296f0d1e5db5885acc83a13a12bb4324e592c9871afbe1" semantic="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `140`
- **范围:** `40` ~ `300`
- **步长:** `5`
- **菜单:** 驾驶控制 \> 巡航与车距 \> 车距
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap3 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap3 -->
<!-- CARROT:REVIEW reviewed-for="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

巡航车距3级的基本跟车时间。增大则基本车距变长，减小则变短。应用速度TF倍率及驾驶、减速修正。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

保存值50表示0.50秒。不同车距级别可设置相同基本TF和不同前车响应。路径上的横条及米数表示动态修正后的跟车目标距离。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap3 -->

<!-- CARROT:SETTING:END TFollowGap3 -->
