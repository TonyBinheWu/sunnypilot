<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_ONNX" param="OnnxLaneIntervalMs" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 車道計算間隔

**選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點

---

<!-- CARROT:SETTING:BEGIN OnnxLaneIntervalMs -->
<a id="OnnxLaneIntervalMs"></a>

## 車道計算間隔

`OnnxLaneIntervalMs`

從道路攝影機再次執行 ONNX 車道推理的最短間隔。

<!-- CARROT:AUTO:BEGIN OnnxLaneIntervalMs -->
<!-- CARROT:AUTO:SOURCE facts="c50b1dcb6e0893d392d390e741b263bb41bb53b3626eec09aadf434c7ff80a9d" semantic="a6072f5036c55f60ab02c7512948ef310595ab36ffe4ce34cabca4fa94f95de1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `400ms`
- **範圍:** `50ms` ~ `2000ms`
- **步長:** `50`
- **顯示單位:** `ms`
- **選單:** 駕駛控制 \> 轉向 \> ONNX 車道與盲點
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxLaneIntervalMs -->

<!-- CARROT:MANUAL:BEGIN OnnxLaneIntervalMs -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END OnnxLaneIntervalMs -->

<!-- CARROT:SETTING:END OnnxLaneIntervalMs -->
