<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="AutoNaviSpeedCtrlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 导航减速模式 (2)

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedCtrlMode -->
<a id="AutoNaviSpeedCtrlMode"></a>

## 导航减速模式 (2)

`AutoNaviSpeedCtrlMode`

0: 不使用, 1: 限速摄像头, 2: 摄像头 + 减速带, 3: 摄像头 + 减速带 + APN 限速摄像头 原车导航 CAN（VehicleNaviCanControl）的移动测速区间（导航蓝色圆圈）也遵循此值：3 时减速，2 及以下忽略移动区间警告。同一警告中若同时存在固定、闯红灯或后向摄像头，则始终减速。

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:AUTO:SOURCE facts="df3710fee95a08a12c7f2eda86687d5e9cbb6de4cfa232fb8c56b6aacc3c06fb" semantic="5b13349929a99c31fde786817313f0a97c7480cf55cdbce1da21739b3610e6d5" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 分段选择
- **默认值:** `2`
- **范围:** `0` ~ `3`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:SETTING:END AutoNaviSpeedCtrlMode -->
