<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaDownLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 变道自定义转向减小斜率(0)

**菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaDownLC -->
<a id="CustomSteerDeltaDownLC"></a>

## 变道自定义转向减小斜率(0)

`CustomSteerDeltaDownLC`

力矩控制车辆 — 变道期间临时应用转向减小斜率 使用 ADAS ECU 的 EV6 HDA2 扭矩转向以每 10 ms 3 个单位的固定速率收回扭矩，驾驶员接管时同样适用。

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:AUTO:SOURCE facts="17a9a0ae8155a63b1dd81103bfe2c0d4f9dc2ad72429f9dcb179a8f6515dfc1f" semantic="24f993369a8dc843e97c8b377086b40d1cb55d05c6cdf714f2e9f859ab68ba73" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0`
- **范围:** `0` ~ `50`
- **步长:** `1`
- **菜单:** 驾驶控制 \> 转向 \> 高级扭矩 \> 转向限制
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaDownLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CustomSteerDeltaDownLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaDownLC -->
