<!-- CARROT:GENERATED schema="1" locale="zh" group="SPEED_CAMERA" param="VehicleNaviDecelCancelBump" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 减速中止：减速带

**菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelBump -->
<a id="VehicleNaviDecelCancelBump"></a>

## 减速中止：减速带

`VehicleNaviDecelCancelBump`

减速中止请求开启时，允许用巡航 + 键或轻踩油门中止原车导航减速带减速。仅在减速带目标速度（由 AutoNaviSpeedBumpSpeed、AutoNaviSpeedBumpTime、AutoNaviSpeedDecelRate 计算）低于设定速度、即实际减速时才使用该输入。中止只适用于最近的一个减速带。

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:AUTO:SOURCE facts="44c7a9d041628b739907874346023551152246c907696b8dd34a1c73c8e5ca7e" semantic="ab15a94879c1067db343091913a6b8ee055f955c0564f0b44795d843826bedfd" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `1`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 速度与减速 \> 测速摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelBump -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelBump -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelBump -->
