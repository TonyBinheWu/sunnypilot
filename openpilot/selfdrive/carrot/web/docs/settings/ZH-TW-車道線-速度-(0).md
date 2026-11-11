<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="UseLaneLineSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車道線: 速度 (0)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN UseLaneLineSpeed -->
<a id="UseLaneLineSpeed"></a>

## 車道線: 速度 (0)

`UseLaneLineSpeed`

超過設定速度時使用車道模式。模型速度軌跡的起點低於實測車速的70%，或終點低於起點的70%時，暫時切換為無車道線模式；正常條件持續約1秒後才可恢復。

<!-- CARROT:AUTO:BEGIN UseLaneLineSpeed -->
<!-- CARROT:AUTO:SOURCE facts="d5978e79385701b438eb9ea96754b6aaacb69e72f2ba47ec15ee5bc162fb4cf7" semantic="9482c046d017df996fafb1a43bed6362e51c89952cf90e9d08991f354560e6f3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0km/h`
- **範圍:** `0km/h` ~ `200km/h`
- **步長:** `1`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseLaneLineSpeed -->

<!-- CARROT:MANUAL:BEGIN UseLaneLineSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END UseLaneLineSpeed -->

<!-- CARROT:SETTING:END UseLaneLineSpeed -->
