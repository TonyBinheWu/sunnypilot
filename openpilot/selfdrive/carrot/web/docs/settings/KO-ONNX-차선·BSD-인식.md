<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_ONNX" param="ShareData" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX 차선·BSD 인식

**메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD

---

<!-- CARROT:SETTING:BEGIN ShareData -->
<a id="ShareData"></a>

## ONNX 차선·BSD 인식

`ShareData`

켜면 comma 장치에서 차선 종류를 인식합니다. 시각 BSD는 별도 OnnxBsdEnabled 설정을 켠 경우에만 실행되며 기본값은 꺼짐입니다. BSD는 모델이 추정한 차로 폭이 2m 이상인 설정된 좌우 영역을 번갈아 검사합니다. 끄면 비전 서비스가 중지되며 차량 자체 BSD는 유지됩니다. 켜져 있어도 onroad 초기화와 모델·CAN·Panda 준비가 완료되어 주행 준비 상태가 0.5초 유지된 뒤 시작합니다. 실제 크루즈 활성화는 필요하지 않습니다. Offroad에서는 종료하고 다음 onroad에서도 다시 기다립니다.

<!-- CARROT:AUTO:BEGIN ShareData -->
<!-- CARROT:AUTO:SOURCE facts="425f6bc25fcb56aa0d4c8f1f6bab986d07228718b22acf17e1d3e68e8d83ebd9" semantic="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShareData -->

<!-- CARROT:MANUAL:BEGIN ShareData -->
<!-- CARROT:REVIEW reviewed-for="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 comma 장치에서 카메라 영상을 받아 실선·점선을 계산하며, `OnnxBsdEnabled`를 함께 켜면 카메라 사각지대도 검사합니다. 끄면 비전 서비스가 멈추며, 차량 자체 BSD는 유지됩니다.

- 차선 종류는 영상을 받는 동안 계속 계산합니다.
- `OnnxBsdEnabled`가 켜져 있을 때 카메라 BSD는 감지 영역을 설정한 쪽 중 모델 추정 차로 폭이 2m 이상인 좌우를 번갈아 검사합니다. 속도와 차로 변경 방향으로 검사를 제한하지 않습니다.

켜져 있어도 onroad 초기화와 모델·CAN·Panda 준비가 완료되어 주행 준비 상태가 0.5초 유지된 뒤 시작됩니다. 실제 크루즈 활성화는 필요하지 않으며, Offroad에서는 종료하고 다음 onroad에서 다시 기다립니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

Carrot Web의 이 스위치로 켜고 끕니다. 기존에 저장한 사용 상태는 유지됩니다. 시작 조건을 만족한 뒤 설정과 mici 표시에는 몇 초 뒤 반영됩니다.

mici의 VISION 카드에서 좌우 차선 종류, 최근 처리 시간, BSD 상태를 확인합니다. 카메라 화면을 숨겨도 카드와 BSD 경고는 표시됩니다.
BSD 벽은 차량 신호만 있으면 노란색, 비전만 있으면 파란색, 둘 다 감지하면 연한 빨간색입니다. 좌우 출처는 각각 표시합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

OpenCV는 업데이트에 포함되며 장치를 정상 시작할 때 로컬 경로에 자동 설치됩니다. 별도 pip 설치는 필요하지 않습니다.

BSD 대기는 아직 해당 방향을 검사하지 않는 상태입니다. 미감지는 전체 사각지대가 안전하다는 뜻이 아니며, 끈 직후의 마지막 결과는 유효 시간이 지나면 사라집니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END ShareData -->

<!-- CARROT:SETTING:END ShareData -->
