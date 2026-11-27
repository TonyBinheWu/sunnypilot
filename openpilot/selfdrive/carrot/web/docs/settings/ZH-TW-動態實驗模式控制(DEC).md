<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DAILY_DRIVING" param="DynamicExperimentalControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 動態實驗模式控制（DEC）

**選單:** 駕駛控制 \> 啟動·自動 \> 日常駕駛

---

<!-- CARROT:SETTING:BEGIN DynamicExperimentalControl -->
<a id="DynamicExperimentalControl"></a>

## 動態實驗模式控制（DEC）

`DynamicExperimentalControl`

使用 openpilot 縱向控制時，下次行程生效。預設關閉，確認前方淨空後由模型在巡航上限內決定加速度。開啟後依路況切換巡航跟車與模型協同。

<!-- CARROT:AUTO:BEGIN DynamicExperimentalControl -->
<!-- CARROT:AUTO:SOURCE facts="58afbd2185e72aa4dbfaa37e44509bc368af3379e065904e623d932a69e51636" semantic="812cd842d2e82c6f1efab61b169f7a27f6ca8a20c4399a0143bf5fb7f7405fcd" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 日常駕駛
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DynamicExperimentalControl -->

<!-- CARROT:MANUAL:BEGIN DynamicExperimentalControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END DynamicExperimentalControl -->

<!-- CARROT:SETTING:END DynamicExperimentalControl -->
