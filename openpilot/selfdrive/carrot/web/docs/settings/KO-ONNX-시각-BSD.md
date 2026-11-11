<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_ONNX" param="OnnxBsdEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX 시각 BSD

**메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD

---

<!-- CARROT:SETTING:BEGIN OnnxBsdEnabled -->
<a id="OnnxBsdEnabled"></a>

## ONNX 시각 BSD

`OnnxBsdEnabled`

와이드 카메라의 ONNX 차량 측면 BSD 인식을 켭니다. 차선 인식과 별도로 동작하며 기본값은 꺼짐입니다. 차량 자체 BSD에는 영향을 주지 않습니다.

<!-- CARROT:AUTO:BEGIN OnnxBsdEnabled -->
<!-- CARROT:AUTO:SOURCE facts="bc8bcfd6a30a7696066997e0cb64ea8924df57f58f1ddc8b33c1414d64868fb9" semantic="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdEnabled -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdEnabled -->
<!-- CARROT:REVIEW reviewed-for="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 와이드 카메라 BSD 모델을 로드하여 설정된 감지 영역 중 모델 추정 차로 폭이 2m 이상인 좌우를 번갈아 검사합니다. 끄면 BSD 모델과 이전 감지 결과를 해제하고 차선 인식은 계속합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

`ShareData`를 켜 비전 서비스가 실행된 상태에서 사용합니다. Carrot Web의 ONNX 상세 화면에서 변경하며 서비스는 약 1초 간격으로 설정을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

차량 자체 BSD에는 영향을 주지 않습니다. 기존에 차선·BSD 인식을 사용했더라도 카메라 BSD를 계속 사용하려면 이 스위치를 별도로 켜야 합니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END OnnxBsdEnabled -->

<!-- CARROT:SETTING:END OnnxBsdEnabled -->
