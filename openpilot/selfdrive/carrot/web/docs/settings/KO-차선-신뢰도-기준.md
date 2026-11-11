<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_ONNX" param="OnnxLaneThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차선 신뢰도 기준

**메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD

---

<!-- CARROT:SETTING:BEGIN OnnxLaneThreshold -->
<a id="OnnxLaneThreshold"></a>

## 차선 신뢰도 기준

`OnnxLaneThreshold`

실선·점선 후보를 유효한 차선으로 판단하는 최소 신뢰도입니다.

<!-- CARROT:AUTO:BEGIN OnnxLaneThreshold -->
<!-- CARROT:AUTO:SOURCE facts="c2b7deea22b2eadf67dabb47db3dbc3e7afe5fc5e003021ac8fdc9f4902339d7" semantic="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `25%`
- **범위:** `0%` ~ `100%`
- **변경 단위:** `1`
- **표시 단위:** `%`
- **메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxLaneThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxLaneThreshold -->
<!-- CARROT:REVIEW reviewed-for="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

높이면 차선 종류를 더 높은 신뢰도에서만 반영하고, 낮추면 불확실한 분류도 더 쉽게 반영합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxLaneThreshold -->

<!-- CARROT:SETTING:END OnnxLaneThreshold -->
