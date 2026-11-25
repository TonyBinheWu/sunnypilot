<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUp" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定义转向增大斜率(0)

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUp -->
<a id="CustomSteerDeltaUp"></a>

## 自定义转向增大斜率(0)

`CustomSteerDeltaUp`

力矩控制车辆 — 值越高方向盘转动速度越快 使用 ADAS ECU 的 EV6 HDA2 扭矩转向每 10 ms 最多增加 2 个单位，也可设置更低的正值。

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:AUTO:SOURCE facts="7cdfe449d252c2cbda642d7ef0216dab08258b27b512d4321ff7405261b93037" semantic="487f32b08b65f588060dd1c924fb762ecab0c2e2bebb4e6c2d3b934e1ca081d3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `50`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUp -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CustomSteerDeltaUp -->

<!-- CARROT:SETTING:END CustomSteerDeltaUp -->
