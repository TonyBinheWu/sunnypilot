<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 右转提示距离（米）

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## 右转提示距离（米）

`AutoTurnControlRightLaneChange`

支持的转向灯适配器在此距离内检查右转或右侧分岔提示。0 米关闭，最高 500 米。适用于 ATC 模式 1 或 2 及自动转向灯模式 2。变道由驾驶人确认。

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="f03ba60d0339cabe72a3d1b33832620ea9ad2c4da27934a68b0706540f9961b9" semantic="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `500`
- **步长:** `50`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

支持的转向灯适配器在此距离内检查右转或右侧分岔提示。0 米关闭，最高 500 米。适用于 ATC 模式 1 或 2 及自动转向灯模式 2。变道由驾驶人确认。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
