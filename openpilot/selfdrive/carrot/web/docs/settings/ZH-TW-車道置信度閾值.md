<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_ONNX" param="OnnxLaneThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車道置信度閾值

**選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點

---

<!-- CARROT:SETTING:BEGIN OnnxLaneThreshold -->
<a id="OnnxLaneThreshold"></a>

## 車道置信度閾值

`OnnxLaneThreshold`

將實線或虛線候選判定為有效車道所需的最低置信度。

<!-- CARROT:AUTO:BEGIN OnnxLaneThreshold -->
<!-- CARROT:AUTO:SOURCE facts="5d07dd49d721d3639bada92443269cbb1bdd0ab9ec2234bc2a274b922a6e1889" semantic="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `25%`
- **範圍:** `0%` ~ `100%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxLaneThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxLaneThreshold -->
<!-- CARROT:REVIEW reviewed-for="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行為

提高此值僅接受置信度更高的車道分類，降低則更容易接受不確定的分類。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxLaneThreshold -->

<!-- CARROT:SETTING:END OnnxLaneThreshold -->
