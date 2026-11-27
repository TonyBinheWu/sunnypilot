<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DAILY_DRIVING" param="SunnyCruisePlanner" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航速度規劃器

**選單:** 駕駛控制 \> 啟動·自動 \> 日常駕駛

---

<!-- CARROT:SETTING:BEGIN SunnyCruisePlanner -->
<a id="SunnyCruisePlanner"></a>

## 巡航速度規劃器

`SunnyCruisePlanner`

下次行程生效。0 保留原規劃器，1 使用 sunnypilot 巡航與車機提供的雷達及視覺前車，2 使用相同巡航規劃且跟車只看攝影機。在實驗模式開啟 DEC 可依路況切換。

<!-- CARROT:AUTO:BEGIN SunnyCruisePlanner -->
<!-- CARROT:AUTO:SOURCE facts="1ddc4aa837f981affba9756f31ff6b8771be1694c701d92196a23b42bbc9bec3" semantic="c38bc552088c099ef8b690307d86f5d076d3fce258662e3c4042e827d3a7bd3d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** 原規劃器 (`0`)
- **範圍:** 原規劃器 (`0`) ~ sunnypilot · 攝影機跟車 (`2`)
- **步長:** `1`
- **選項:** `0` 原規劃器, `1` sunnypilot · 車輛感測器, `2` sunnypilot · 攝影機跟車
- **選單:** 駕駛控制 \> 啟動·自動 \> 日常駕駛
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SunnyCruisePlanner -->

<!-- CARROT:MANUAL:BEGIN SunnyCruisePlanner -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SunnyCruisePlanner -->

<!-- CARROT:SETTING:END SunnyCruisePlanner -->
