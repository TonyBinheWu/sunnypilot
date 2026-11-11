<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="AutoBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自动转向灯

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN AutoBlinkerControl -->
<a id="AutoBlinkerControl"></a>

## 自动转向灯

`AutoBlinkerControl`

0：关闭（保留蓝牙轻触）。1：低于5km/h蓝牙保持至转弯结束，从ATC audioTurn提示开始保持，路口停车时不熄灭，实际转弯后方向盘回正时解除。2：另含实际开始的ATC变道，等待时不亮。同方向取消保持，反方向切换。原车拨杆优先。需要支持的Jetson USB-CAN/B1车辆。 ATC在确认发送完成但未亮灯时最多重试一次。有效TBT坐标与车辆GPS确认直行通过后自动取消；位置不可靠时不使用该位置取消判断。 TBT按audioTurn距离及行驶距离跟踪至转弯点后30米。确认对应方向转角超过30度且车身方向变化至少20度后，车速至少1km/h时方向盘回到±15度以内立即结束保持。进入转弯前的信号灯停车仍保持。新的下一转弯提示在当前转弯结束后接续；对应方向转角达到30度后，驾驶员反向施力使转角越过零点进入反方向时取消。已确认发送及亮灯的TBT保持不因接收端driver\_override状态单独解除。不能保证原车灯立即熄灭。 按巡航 CANCEL 会停止自动转向灯请求并解除自动保持。泊车转动方向盘不会重新触发；用 SET/RES 或 +/− 解除巡航取消状态后，新动作才可触发。原车拨杆和蓝牙转向灯按钮仍可手动使用。

<!-- CARROT:AUTO:BEGIN AutoBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="746d97b59d9aa5567e7800090c8265dc03e28b7d162065af32348bc750a3adc5" semantic="edd05659292aebc71be712906d3faaadf71c30551e5a372287abb2bf65bd60ca" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `0`
- **范围:** `0` ~ `2`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN AutoBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="edd05659292aebc71be712906d3faaadf71c30551e5a372287abb2bf65bd60ca" reviewed-at="2026-11-10T10:39:14.890627+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

在支持的车辆上管理BT和ATC实际转向灯请求及保持。

确认进入转弯后，行驶中方向盘回到±15度以内即正常结束，也使用转弯点后的行驶距离判断结束。对应方向转角达到30度后，驾驶员反向施力使转角越过零点进入反方向时取消。

已确认发送及亮灯的TBT保持可在接收端driver_override状态下继续至转弯结束。缺少首次发送确认时无法启用保持。新的下一转弯提示在当前转弯结束后接续。

按巡航 CANCEL 会停止自动转向灯请求并解除自动保持。泊车转动方向盘不会重新触发；用 SET/RES 或 +/− 解除巡航取消状态后，新动作才可触发。原车拨杆和蓝牙转向灯按钮仍可手动使用。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoBlinkerControl -->

<!-- CARROT:SETTING:END AutoBlinkerControl -->
