<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: 自动转向控制

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC: 自动转向控制

`AutoTurnControl`

0: 关闭，1: 变道/转弯，2: 变道/转弯+速度，3: 速度。右转前自动变道距离在详细设置中调整，0米关闭，仅在模式1或2下工作。

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="3d0e31c8b1f9f8ea943a70ef47c4b99a502d197a20beec1975fd764860a7f31b" semantic="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `3`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" reviewed-at="2026-11-02T22:15:29.548185+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

0关闭ATC，1控制变道和转弯，2同时控制速度，3仅控制速度。右转距离附加功能在模式1或2下于设定距离内请求右转向灯。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

在ATC详细设置中选择右转前自动变道距离。增大距离会更早检查条件，减小距离则靠近转弯后检查。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

重启时旧模式4转换为模式1。没有单独距离设置时使用250米，已明确设置的值予以保留。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
