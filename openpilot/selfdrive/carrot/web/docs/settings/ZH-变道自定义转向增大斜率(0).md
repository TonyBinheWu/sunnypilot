<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUpLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 变道自定义转向增大斜率(0)

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUpLC -->
<a id="CustomSteerDeltaUpLC"></a>

## 变道自定义转向增大斜率(0)

`CustomSteerDeltaUpLC`

力矩控制车辆 — 变道期间临时应用转向增大斜率 使用 ADAS ECU 的 EV6 HDA2 扭矩转向每 10 ms 最多增加 2 个单位，也可设置更低的正值。

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:AUTO:SOURCE facts="8db2b25bf35bf0e6507a8a6a7cb367d8c02e3bad98c55fe2dbb256702c9ca6b5" semantic="a269ff8291eb110176550d7c9962c300e661cb8701b0d25780bbf6bd978c1ba5" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `50`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUpLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CustomSteerDeltaUpLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaUpLC -->
