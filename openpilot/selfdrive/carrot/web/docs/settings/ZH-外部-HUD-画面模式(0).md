<!-- CARROT:GENERATED schema="1" locale="zh" group="HUD_SCREEN" param="ClusterHudScreenMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 画面模式(0)

**菜单:** 显示 \> 外部HUD \> 画面·摄像头

---

<!-- CARROT:SETTING:BEGIN ClusterHudScreenMode -->
<a id="ClusterHudScreenMode"></a>

## 外部 HUD 画面模式(0)

`ClusterHudScreenMode`

-1: 3D全屏 0: 默认(导航/驾驶报告) 1: 调试 2: 调试(系统) 3: 调试(图表1) 4: 调试(图表2) 5: 驾驶报告 6: 外部导航全屏 7: 驾驶画面 + 右侧Nav地图 Onroad 状态下，P 挡优先显示驻车画面，R 挡显示基于 EV6 尺寸的倒车参考图。其他挡位或 offroad 恢复原画面模式。

<!-- CARROT:AUTO:BEGIN ClusterHudScreenMode -->
<!-- CARROT:AUTO:SOURCE facts="3bd735c9ea5a8877b5bf6bdeb9a7d1c4f55af7bc1749f023e964fa1b1d1fbeae" semantic="4454f6bc7bf3c1b0d27dc7adfae91475bc67670dc85dee7fee357a165b54433d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** `0`
- **范围:** `-1` ~ `7`
- **步长:** `1`
- **菜单:** 显示 \> 外部HUD \> 画面·摄像头
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudScreenMode -->

<!-- CARROT:MANUAL:BEGIN ClusterHudScreenMode -->
<!-- CARROT:REVIEW reviewed-for="627a973ecafa1b31a96e570c3d02499497c8b6d45ab1e2366aa65ab21435fe93" reviewed-at="2026-07-31T23:37:31+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

- `-1` — 在 3D 摄像头视图 `0`、`1` 中取消信息面板并使用全屏宽度。左侧项目保持原边距，右侧仪表和 TPMS 对齐物理屏幕右边缘，时钟、3D 场景和转向灯以全屏中心为轴。在道路摄像头视图 `2` 中，导航/驾驶报告自动切换和左右面板布局与模式 `0` 完全相同。
- `0` — 默认画面；收到导航时显示导航面板，否则自动显示驾驶报告。
- `1` — 显示延迟、扭矩、转向和横向规划状态的实时调试画面。
- `2` — 基准系统画面；不使用模式 `0` 的自动驾驶报告回退，有导航状态时保持导航或 `NAVI DISCONNECTED`，仅在没有导航来源时显示路线叠加层。
- `3` — 关闭驾驶场景并放大显示 `ShowPlotMode` 图表。
- `4` — 保留驾驶场景并在信息面板中显示图表。加速度、转向、燃油和 DEF 仪表紧靠图表左侧并随面板左右切换，TPMS 保留在驾驶画面一侧。
- `5` — 始终显示驾驶报告。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用

日常自动导航/报告使用 `0`，需要更宽的 3D 场景时使用 `-1`，需要同时比较驾驶场景和图表时使用 `4`。要恢复普通自动画面，请重新选择 `0`。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudScreenMode -->

<!-- CARROT:SETTING:END ClusterHudScreenMode -->
