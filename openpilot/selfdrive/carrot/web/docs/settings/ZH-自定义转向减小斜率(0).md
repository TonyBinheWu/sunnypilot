<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaDown" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定义转向减小斜率(0)

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaDown -->
<a id="CustomSteerDeltaDown"></a>

## 自定义转向减小斜率(0)

`CustomSteerDeltaDown`

力矩控制车辆 — 值越高方向盘回正速度越快 使用 ADAS ECU 的 EV6 HDA2 扭矩转向以每 10 ms 3 个单位的固定速率收回扭矩，驾驶员接管时同样适用。

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaDown -->
<!-- CARROT:AUTO:SOURCE facts="c280da374a8e108bd2ba905f060c280fcf0e69c1530a5b44edba1365f2f11265" semantic="a804ff8b309581e89bebde4f8a28234c43931ae219c283217df3cfec42cf2e44" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `50`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaDown -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaDown -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CustomSteerDeltaDown -->

<!-- CARROT:SETTING:END CustomSteerDeltaDown -->
