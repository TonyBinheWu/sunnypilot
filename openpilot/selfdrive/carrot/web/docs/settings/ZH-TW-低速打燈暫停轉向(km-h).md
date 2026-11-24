<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DAILY_DRIVING" param="SunnyBlinkerPauseKph" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 低速打燈暫停轉向（km/h）

**選單:** 駕駛控制 \> 啟動·自動 \> 日常駕駛

---

<!-- CARROT:SETTING:BEGIN SunnyBlinkerPauseKph -->
<a id="SunnyBlinkerPauseKph"></a>

## 低速打燈暫停轉向（km/h）

`SunnyBlinkerPauseKph`

模型與跟車協同模式，下次行程生效。0 為關閉。低於設定時速且單側打燈時暫停轉向；燈號結束後依原有接合條件恢復。

<!-- CARROT:AUTO:BEGIN SunnyBlinkerPauseKph -->
<!-- CARROT:AUTO:SOURCE facts="d079ba5611ec889b4634387354cea02a7a29e4921150dd9537557f9b40ba651f" semantic="49fff7c9b8de6f29293c0c3f9603a7ed153258de03b3b3f959c81becee0952ed" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `30`
- **步長:** `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 日常駕駛
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SunnyBlinkerPauseKph -->

<!-- CARROT:MANUAL:BEGIN SunnyBlinkerPauseKph -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SunnyBlinkerPauseKph -->

<!-- CARROT:SETTING:END SunnyBlinkerPauseKph -->
