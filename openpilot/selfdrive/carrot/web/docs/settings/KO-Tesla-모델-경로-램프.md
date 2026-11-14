<!-- CARROT:GENERATED schema="1" locale="ko" group="TESLA_FEATURES" param="TeslaModelPathSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla 모델 경로 램프

**메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능

---

<!-- CARROT:SETTING:BEGIN TeslaModelPathSignals -->
<a id="TeslaModelPathSignals"></a>

## Tesla 모델 경로 램프

`TeslaModelPathSignals`

Tesla 자동 방향지시등·데이터 공유가 필요합니다. 횡제어 활성·30km/h 이상에서 차선 곡률 대비 모델 경로의 반복된 경계 통과 예측과 ONNX 점선·인접 차로 형상으로 램프만 요청합니다. 의도 예측과 독립적인 기본 꺼짐 옵션입니다. 내비 회전 사전점등·유턴을 추가하지 않습니다. 오점등 가능, 조향 권한 불변. 변경 후 재부팅·폐쇄 시험장 검증 필요.

<!-- CARROT:AUTO:BEGIN TeslaModelPathSignals -->
<!-- CARROT:AUTO:SOURCE facts="a7a2af245bc4c2ff8ba415b5bf5ef5dc442a68d15396e3b6ceae2bab6b294dd0" semantic="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelPathSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelPathSignals -->
<!-- CARROT:REVIEW reviewed-for="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" reviewed-at="2026-11-08T01:13:19.735208+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 곡선 차선 대비 모델 경로의 반복된 경계 통과 예측으로 램프를 요청하고 끄면 이 예측을 사용하지 않습니다. 서로 다른 프레임 최소 4개·0.2초, 횡제어 활성·30km/h·신선한 ONNX 점선/인접 차로 근거가 필요하며 모델·조향 명령은 바꾸지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

Tesla 자동 방향지시등·데이터 공유·지원 CAN/스토크/피드백이 필요하며 변경 후 재부팅합니다. 수동·의도 옵션과 독립적이고 ATC/App이 우선합니다. 근거·상태 상실, 복귀·완료·12초에 기존 실행기로 취소하며 재시작에는 중립 예측과 소등 재확인이 필요합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

미리 또는 잘못 점등할 수 있으며 모든 통과를 감지하지 못합니다. 서로 다른 점선 2회·0.2초와 완료 나이 0.8초 이내가 필요하며 촬영 나이는 아닙니다. 기본 400ms는 유지합니다. 점선은 색상·진행 방향·빈 공간 증거가 아닙니다. 내비 회전 사전점등·회전 예측·유턴 구현은 없으며 폐쇄 시험장 실차 확인은 미완료입니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelPathSignals -->

<!-- CARROT:SETTING:END TeslaModelPathSignals -->
