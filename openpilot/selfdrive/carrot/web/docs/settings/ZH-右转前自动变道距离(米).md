<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 右转前自动变道距离(米)

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## 右转前自动变道距离(米)

`AutoTurnControlRightLaneChange`

0米关闭，在设定距离内检查条件。250米对应原有范围，也可选择300–400米。原开启设置在启动时转换为250米。附加于ATC模式1或2。车速至少10km/h时，距TBT右转或右侧分岔设定距离以内且尚未开始转弯时请求右转向灯。需要Ioniq 5 PE USB2CAN、AutoBlinkerControl=2及LaneChangeNeedTorque=0。后方仅检查有效原车BSD警告，不使用角雷达距离。右侧目标车道的前方车辆当前距离及按相对速度预测3秒后的距离均须至少5米。前雷达故障或数据过期时不启动。请求前转向会重新确认条件，请求后驾驶员干预会取消。 低于30km/h开始的信号始终仅作显示；至少30km/h开始时才进入既有变道流程。右侧车道线到道路边缘须至少2.5米。

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="1ef251bdf4ed77a75adec8ba99c887ca893b07f5c36bc58023c1fa7723c3a510" semantic="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `500`
- **步长:** `50`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" reviewed-at="2026-11-02T22:15:29.552199+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

0米关闭附加功能，增大数值会在右转或右侧分岔前更远处检查条件。250米对应原有范围，原开启设置在重启时转换为250米。

车速至少10km/h时检查右侧车道、道路边缘、有效BSD及当前和3秒预测前车距离。低于30km/h开始的信号仅作显示，达到30km/h时开始的信号进入既有变道判断。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
