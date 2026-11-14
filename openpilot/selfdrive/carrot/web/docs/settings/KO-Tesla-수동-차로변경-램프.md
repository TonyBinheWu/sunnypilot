<!-- CARROT:GENERATED schema="1" locale="ko" group="TESLA_FEATURES" param="TeslaManualLaneSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla 수동 차로변경 램프

**메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능

---

<!-- CARROT:SETTING:BEGIN TeslaManualLaneSignals -->
<a id="TeslaManualLaneSignals"></a>

## Tesla 수동 차로변경 램프

`TeslaManualLaneSignals`

Tesla 자동 방향지시등과 데이터 공유가 필요합니다. 30km/h 이상에서 운전자 조향 의도·차선 접근과 ONNX의 연속된 점선 분류·인접 차로 형상을 확인해 좌우 램프만 요청합니다. 크루즈 비활성도 허용하나 조향 권한은 늘리지 않습니다. 실선·불명·오래된 결과는 새 요청을 차단합니다. 차선 색상·진행 방향은 판별하지 못합니다. 기본 꺼짐, 변경 후 재부팅; 폐쇄 시험장 검증 필요.

<!-- CARROT:AUTO:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:AUTO:SOURCE facts="d194268420c3481a101512fa6a1fbf2df9b4e2838e88270828c4874b65464e45" semantic="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaManualLaneSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:REVIEW reviewed-for="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" reviewed-at="2026-11-08T01:13:19.689868+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 운전자 토크와 양쪽 경계 접근을 관찰해 크루즈 없이 좌우 램프만 요청하고, 끄면 기존 ATC/App 램프만 유지합니다. 좌우 모두 30km/h 이상·신선한 연속 ONNX 점선·인접 차로 형상·도로 경계 여유가 필요하며 조향 desire는 쓰지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

Tesla 자동 방향지시등·데이터 공유·지원 차량 CAN·실제 스토크와 램프 피드백이 필요하며 변경 후 재부팅합니다. 시각 BSD는 별개입니다. 운전자·비상등·무효 상태·근거 상실·복귀·통과 완료 또는 12초 후 기존 취소/OFF 확인으로 종료합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

서로 다른 점선 완료 시각 2회가 0.2초 이상 이어지고 현재 0.8초 이내여야 하며 기본 추론 400ms는 유지합니다. 완료 시각은 촬영 시각이 아닙니다. 점선은 흰색·같은 진행 방향·빈 공간의 증거가 아닙니다. 내비 회전 사전점등·거리 추가·유턴 구현은 없고 타이어 통과 전 점등을 보장하지 않습니다. 폐쇄 시험장 실차 확인이 필요합니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaManualLaneSignals -->

<!-- CARROT:SETTING:END TeslaManualLaneSignals -->
