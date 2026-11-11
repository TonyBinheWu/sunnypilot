<!-- CARROT:GENERATED schema="1" locale="zh" group="STEER_ONNX" param="OnnxLaneThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 车道置信度阈值

**菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点

---

<!-- CARROT:SETTING:BEGIN OnnxLaneThreshold -->
<a id="OnnxLaneThreshold"></a>

## 车道置信度阈值

`OnnxLaneThreshold`

将实线或虚线候选判定为有效车道所需的最低置信度。

<!-- CARROT:AUTO:BEGIN OnnxLaneThreshold -->
<!-- CARROT:AUTO:SOURCE facts="7f136387b15ed6fd242bfdf194e721c968828d9f2da8d2ffaeb2dae0553840ad" semantic="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `25%`
- **范围:** `0%` ~ `100%`
- **步长:** `1`
- **显示单位:** `%`
- **菜单:** 驾驶控制 \> 转向 \> ONNX 车道与盲点
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxLaneThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxLaneThreshold -->
<!-- CARROT:REVIEW reviewed-for="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 行为

提高此值仅接受置信度更高的车道分类，降低则更容易接受不确定的分类。
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxLaneThreshold -->

<!-- CARROT:SETTING:END OnnxLaneThreshold -->
