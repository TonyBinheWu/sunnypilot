<!-- CARROT:GENERATED schema="1" locale="zh" group="VEH_RADAR" param="EnableRadarTracks" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 开启雷达轨迹 (0)

**菜单:** 车辆与硬件 \> 雷达

---

<!-- CARROT:SETTING:BEGIN EnableRadarTracks -->
<a id="EnableRadarTracks"></a>

## 开启雷达轨迹 (0)

`EnableRadarTracks`

-2: VOACC 纯视觉测试 -1: 无视觉匹配始终使用 SCC；无 SCC 时使用视觉 0: 始终使用 SCC 纵向距离和相对速度；无 SCC 时使用视觉 1: 仅前雷达与视觉匹配；失败时使用视觉 2: 前雷达 + 低速 SCC 与视觉匹配；失败时使用视觉 3: 前雷达视觉匹配失败后始终使用 SCC；无 SCC 时使用视觉 新视觉目标要求 prob \>= 0.40；所有 SCC 匹配均忽略横向位置 自动支持传统 Mando 32/64 槽位版本

<!-- CARROT:AUTO:BEGIN EnableRadarTracks -->
<!-- CARROT:AUTO:SOURCE facts="d2673d15516ce2d1b33d40a1a192ccc3f051c9234d1ac1800e4eeb486a7ff718" semantic="0aab8f5fa0c29c37fd4b650cd2a25ffe0451f1c62b9f8fcbcb386721f8c81218" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 选择
- **默认值:** `0`
- **范围:** `-2` ~ `3`
- **步长:** `1`
- **菜单:** 车辆与硬件 \> 雷达
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableRadarTracks -->

<!-- CARROT:MANUAL:BEGIN EnableRadarTracks -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END EnableRadarTracks -->

<!-- CARROT:SETTING:END EnableRadarTracks -->
