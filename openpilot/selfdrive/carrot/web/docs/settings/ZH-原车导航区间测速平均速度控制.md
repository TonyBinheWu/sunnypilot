<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviSectionAvgControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 原车导航区间测速平均速度控制

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSectionAvgControl -->
<a id="VehicleNaviSectionAvgControl"></a>

## 原车导航区间测速平均速度控制

`VehicleNaviSectionAvgControl`

仅在外部导航未连接时应用。原车导航 CAN 区间测速期间照常固定在区间限速（× 安全系数）。openpilot 启用且巡航设定速度高于该上限时，按一次巡航 + 键或轻踩油门即解除该区间的固定，仅在进入区间后的平均速度保持在区间限速以下的范围内允许达到设定速度。只能使用因拥堵等积累的余量；没有余量时与原限制相同。此输入不会提高设定速度。长按巡航 - 键重新固定且不改变设定速度（短按仍照常降低设定速度），离开区间时复位。终点摄像头约提前 2km 预告后按点位减速。区间起点取平均速度信号出现的时刻，为实验功能。

<!-- CARROT:AUTO:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:AUTO:SOURCE facts="7c3d91920081f52569619c204bae7d216dfdee0ad36a93c1fbcb27e4e1244a91" semantic="279eeacf277d306a733765fc4b26354220278af698c6266e606d727260d2e3ec" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSectionAvgControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviSectionAvgControl -->

<!-- CARROT:SETTING:END VehicleNaviSectionAvgControl -->
