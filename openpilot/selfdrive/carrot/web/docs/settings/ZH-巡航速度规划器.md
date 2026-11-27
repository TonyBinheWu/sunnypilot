<!-- CARROT:GENERATED schema="1" locale="zh" group="DAILY_DRIVING" param="SunnyCruisePlanner" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航速度规划器

**菜单:** 驾驶控制 \> 启动·自动 \> 日常驾驶

---

<!-- CARROT:SETTING:BEGIN SunnyCruisePlanner -->
<a id="SunnyCruisePlanner"></a>

## 巡航速度规划器

`SunnyCruisePlanner`

下次行程生效。0 为原规划器，1 用 sunnypilot 巡航与车辆提供的雷达和视觉前车，2 用同一规划器且跟车只用摄像头。开启 DEC 后可在实验模式下依路况切换。

<!-- CARROT:AUTO:BEGIN SunnyCruisePlanner -->
<!-- CARROT:AUTO:SOURCE facts="4abcf8959707881904fda4850ed8952af462057457449b67c9117d87c6e6712b" semantic="c38bc552088c099ef8b690307d86f5d076d3fce258662e3c4042e827d3a7bd3d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** 原规划器 (`0`)
- **范围:** 原规划器 (`0`) ~ sunnypilot · 摄像头跟车 (`2`)
- **步长:** `1`
- **选项:** `0` 原规划器, `1` sunnypilot · 车辆传感器, `2` sunnypilot · 摄像头跟车
- **菜单:** 驾驶控制 \> 启动·自动 \> 日常驾驶
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SunnyCruisePlanner -->

<!-- CARROT:MANUAL:BEGIN SunnyCruisePlanner -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SunnyCruisePlanner -->

<!-- CARROT:SETTING:END SunnyCruisePlanner -->
