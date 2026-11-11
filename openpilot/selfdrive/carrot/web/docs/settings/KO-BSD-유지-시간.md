<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_ONNX" param="OnnxBsdSmoothingMs" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# BSD 유지 시간

**메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD

---

<!-- CARROT:SETTING:BEGIN OnnxBsdSmoothingMs -->
<a id="OnnxBsdSmoothingMs"></a>

## BSD 유지 시간

`OnnxBsdSmoothingMs`

BSD 신뢰도를 평활화하며 활성화 후에는 시작 기준보다 15%p 낮아질 때 해제합니다.

<!-- CARROT:AUTO:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:AUTO:SOURCE facts="e2637601c39d2e9ef202c9a41cc608fbea1985f029b891791797f984b0fc63ba" semantic="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `200ms`
- **범위:** `100ms` ~ `500ms`
- **변경 단위:** `100`
- **표시 단위:** `ms`
- **메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdSmoothingMs -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:REVIEW reviewed-for="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

높이면 BSD 신뢰도 평활화가 느려지고, 낮추면 새 결과를 더 빠르게 반영합니다. 활성화 이후 해제 기준은 활성화 기준보다 15%p 낮으며 0 아래로 내려가지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdSmoothingMs -->

<!-- CARROT:SETTING:END OnnxBsdSmoothingMs -->
