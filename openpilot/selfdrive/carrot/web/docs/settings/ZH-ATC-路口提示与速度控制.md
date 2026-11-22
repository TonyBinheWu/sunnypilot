<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC 路口提示与速度控制

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC 路口提示与速度控制

`AutoTurnControl`

0 关闭，1 路口提示，2 路口提示与速度控制，3 速度控制。导航显示出口和转弯提示，变道方向由驾驶人选择。

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="f0126f44b86dca328563912abde4c22847b08a15d3ae5fcb509dd7393860e9e6" semantic="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `3`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

0 关闭，1 路口提示，2 路口提示与速度控制，3 速度控制。导航显示出口和转弯提示，变道方向由驾驶人选择。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

模式 1 提供路口提示，模式 2 同时控制转弯速度，模式 3 只控制速度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

变道前先检查相邻车道，再打对应方向灯。
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
