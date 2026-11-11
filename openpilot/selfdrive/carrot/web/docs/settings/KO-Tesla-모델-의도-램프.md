<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_START" param="TeslaModelDesireSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla 모델 의도 램프

**메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작

---

<!-- CARROT:SETTING:BEGIN TeslaModelDesireSignals -->
<a id="TeslaModelDesireSignals"></a>

## Tesla 모델 의도 램프

`TeslaModelDesireSignals`

Tesla 자동 방향지시등·데이터 공유가 필요합니다. 횡제어 활성·30km/h 이상에서 반복된 모델 차로변경 예측과 ONNX 점선·인접 차로 형상으로 램프만 미리 요청합니다. 수동 램프와 독립적인 기본 꺼짐 옵션입니다. 회전 내비 안내·유턴은 대상이 아닙니다. 예측 오점등 가능, 조향 권한 불변. 변경 후 재부팅·폐쇄 시험장 검증 필요.

<!-- CARROT:AUTO:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:AUTO:SOURCE facts="20c4d36828baab210b5afa26d44e64c071e8890c00d04969e57a1f18d3d2aa28" semantic="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelDesireSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:REVIEW reviewed-for="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" reviewed-at="2026-11-08T01:13:19.715936+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 우세한 차로변경 확률이 서로 다른 모델 프레임 최소 4개·0.2초 이상 이어질 때 램프를 요청하고 끄면 이 예측을 사용하지 않습니다. 횡제어 활성·30km/h·수동 램프와 같은 신선한 ONNX 점선/인접 차로 근거가 필요하며 조향 요청은 만들지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

Tesla 자동 방향지시등·데이터 공유·지원 차량 CAN/스토크/피드백이 필요하며 변경 후 재부팅합니다. 수동·경로 옵션과 독립적이고 기존 ATC/App 의도가 우선합니다. 근거 상실·완료·복귀·12초에 취소하며 연속 예측은 중립 예측과 소등 재확인 없이 소비한 관찰을 재실행하지 않습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

미리 또는 잘못 점등할 수 있습니다. 서로 다른 점선 2회·0.2초와 완료 나이 0.8초 이내가 필요하며 촬영 나이 상한은 아닙니다. 기본 추론 400ms는 유지합니다. 색상·진행 방향·빈 공간 증거와 내비 회전 사전점등·회전 예측·유턴 구현은 없습니다. PC 검증은 실차 검증이 아닙니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelDesireSignals -->

<!-- CARROT:SETTING:END TeslaModelDesireSignals -->
