<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_FEEL" param="LowSpeedRadarGuard" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速近距雷达辅助

**菜单:** 驾驶控制 \> 转向 \> 转向手感

---

<!-- CARROT:SETTING:BEGIN LowSpeedRadarGuard -->
<a id="LowSpeedRadarGuard"></a>

## 低速近距雷达辅助

`LowSpeedRadarGuard`

15 km/h 以下，前方雷达连续确认接近目标时限制正加速度。侧方占用或雷达失效时暂缓新的自动转弯请求。无法量测墙面净距。

<!-- CARROT:AUTO:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:AUTO:SOURCE facts="4233324b0966f0a82e9652be767ce96e1f03b1c379d93046d195b81c472bb659" semantic="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 开关
- **默认值:** `0`
- **范围:** `0` ~ `1`
- **菜单:** 驾驶控制 \> 转向 \> 转向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedRadarGuard -->

<!-- CARROT:MANUAL:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:REVIEW reviewed-for="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" reviewed-at="2026-11-27T22:32:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 工作方式

同一前方目标须在 7 米内，以超过 0.5 米/秒的相对速度接近，预计接触时间不超过 2 秒，并连续出现在三笔不同的雷达数据中。触发后限制正加速，保留更强的减速要求。侧方没有目标时，需要现代或起亚 0x180 或 0x235 角雷达一次完整且新鲜的扫描才能解除侧方限制。墙面和路缘可能在探测范围以外。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LowSpeedRadarGuard -->

<!-- CARROT:SETTING:END LowSpeedRadarGuard -->
