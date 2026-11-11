<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviDecelCancelMobileZone" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 减速中止：移动测速区间

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelMobileZone -->
<a id="VehicleNaviDecelCancelMobileZone"></a>

## 减速中止：移动测速区间

`VehicleNaviDecelCancelMobileZone`

减速中止请求开启时，允许用巡航 + 键或轻踩油门中止移动测速区间（导航蓝色圆圈）的减速。导航减速模式（AutoNaviSpeedCtrlMode）为 3 时移动区间才会减速，模式 2 及以下不生效。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:AUTO:SOURCE facts="8a23742c348875aba6d0d357610d5ba949582640d7050d382689ff0657437b6a" semantic="570b00e282ceb2973c52e7d7121aea5fd059e453aac9b714b972da032891c62e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `1`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelMobileZone -->
