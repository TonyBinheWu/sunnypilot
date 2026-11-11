<!-- CARROT:GENERATED schema="1" locale="zh" group="CRUISE_CARROT" param="CruiseCoastingPercent" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航滑行余量

**菜单:** 驾驶控制 \> 巡航与车距 \> Carrot巡航

---

<!-- CARROT:SETTING:BEGIN CruiseCoastingPercent -->
<a id="CruiseCoastingPercent"></a>

## 巡航滑行余量

`CruiseCoastingPercent`

0%保持原有控制。在超过设定速度时减弱巡航减速，接近余量上限时恢复减速。不提高设定速度，也不关闭SCC。仅在无前车、停车或外部速度控制介入的普通巡航中生效。

<!-- CARROT:AUTO:BEGIN CruiseCoastingPercent -->
<!-- CARROT:AUTO:SOURCE facts="aacd2e5d376a1f801269d875a1fec89f64c0c5abb8fef7f6ccb78bd179d0238f" semantic="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `0%`
- **范围:** `0%` ~ `10%`
- **步长:** `1`
- **显示单位:** `%`
- **菜单:** 驾驶控制 \> 巡航与车距 \> Carrot巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseCoastingPercent -->

<!-- CARROT:MANUAL:BEGIN CruiseCoastingPercent -->
<!-- CARROT:REVIEW reviewed-for="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" reviewed-at="2026-09-25T08:35:39+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

仅在普通巡航超过设定速度时减弱减速指令。提高此值会扩大允许超速的区间，降低此值会更早恢复正常减速。

- 区间前10%逐渐增加滑行余量，最后40%逐渐恢复正常减速。不提高设定速度或MPC目标，也不关闭SCC。
- 要求基准速度超过10km/h，设定速度、余量设置及允许条件保持一秒。进入允许条件时固定换算后的基准速度；之后速度换算比例的变化不会重置等待时间或移动基准。
- 前车、切入候选、停车、弯道限制、外部速度控制、变道及实验模式均禁止滑行补偿。设定速度或余量改变、或允许条件解除后，需要重新确定基准并等待一秒。
- 节能控制提高目标速度期间及现有CarrotCruise加速限制模式中不生效。导航限速不高于滑行上限时也不生效。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

运行期间约每秒读取一次设置。选择关闭值可恢复原有巡航减速控制。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 参考

设定速度100km/h、余量5%时，在103至105km/h之间恢复正常减速。此功能不会主动加速至105km/h，也不保证实际速度绝不超过上限。

SCC零加速度请求仍可能产生能量回收，具体取决于车辆。尚未完成实车行驶验证。
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseCoastingPercent -->

<!-- CARROT:SETTING:END CruiseCoastingPercent -->
