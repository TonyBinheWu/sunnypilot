<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_LANECHANGE" param="LaneChangeLeverWait" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 单触变道请求等待 5 次闪烁

**菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)

---

<!-- CARROT:SETTING:BEGIN LaneChangeLeverWait -->
<a id="LaneChangeLeverWait"></a>

## 单触变道请求等待 5 次闪烁

`LaneChangeLeverWait`

仅限现代 CAN-FD（0x3C1 拨杆信号）。单触拨杆后若变道未立即获批（BSD、侧方车辆、车道线等原有判断），从拨杆起保持转向灯并等待 5 次闪烁（约 4 秒）。期间解除则变道，否则放弃请求，剩余闪烁不会再触发。锁定拨杆时照旧持续等待。

<!-- CARROT:AUTO:BEGIN LaneChangeLeverWait -->
<!-- CARROT:AUTO:SOURCE facts="1a67e2b852b4a69fd4e9b0eff065bb38487bb45546e12970cd59b347aa20de67" semantic="ea223332818ad995bfa4b772614a0e20f4c64f676f70ec1be8afd5eb871ae2db" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 变道 (自动转向)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeLeverWait -->

<!-- CARROT:MANUAL:BEGIN LaneChangeLeverWait -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END LaneChangeLeverWait -->

<!-- CARROT:SETTING:END LaneChangeLeverWait -->
