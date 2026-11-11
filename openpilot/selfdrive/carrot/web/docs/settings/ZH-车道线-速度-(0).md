<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANEMODE" param="UseLaneLineSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 车道线: 速度 (0)

**菜单:** 驾驶控制 \> 转向 \> 车道模式

---

<!-- CARROT:SETTING:BEGIN UseLaneLineSpeed -->
<a id="UseLaneLineSpeed"></a>

## 车道线: 速度 (0)

`UseLaneLineSpeed`

超过设定速度时使用车道模式。模型速度轨迹的起点低于实测车速的70%，或终点低于起点的70%时，暂时切换为无车道线模式；正常条件持续约1秒后才可恢复。

<!-- CARROT:AUTO:BEGIN UseLaneLineSpeed -->
<!-- CARROT:AUTO:SOURCE facts="bf8af05c694a90f7cc72381d17e39bd5363dfc9a4a6f5d6f005f133f647134db" semantic="9482c046d017df996fafb1a43bed6362e51c89952cf90e9d08991f354560e6f3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0km/h`
- **范围:** `0km/h` ~ `200km/h`
- **步长:** `1`
- **显示单位:** `km/h`
- **菜单:** 驾驶控制 \> 转向 \> 车道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseLaneLineSpeed -->

<!-- CARROT:MANUAL:BEGIN UseLaneLineSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END UseLaneLineSpeed -->

<!-- CARROT:SETTING:END UseLaneLineSpeed -->
