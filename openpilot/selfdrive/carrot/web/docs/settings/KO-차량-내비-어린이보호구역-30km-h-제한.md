<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviSchoolZoneControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차량 내비 어린이보호구역 30km/h 제한

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSchoolZoneControl -->
<a id="VehicleNaviSchoolZoneControl"></a>

## 차량 내비 어린이보호구역 30km/h 제한

`VehicleNaviSchoolZoneControl`

외부 내비가 연결되지 않았을 때만 적용합니다. 외부 내비 연결 중에는 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 차량 순정 내비 CAN에서 확인된 30km/h 제한구역 진입 신호를 받으면 제한구역을 벗어날 때까지 목표 속도를 30km/h 이하로 제한합니다. 일반 30km/h 제한구역에도 적용될 수 있는 실험 기능이며 PV5에서는 아직 동작하지 않습니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:AUTO:SOURCE facts="8cbfeafc4711b1bb6be09e75ab45cab9ecb755d734d81aa64932e392d377c9bb" semantic="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:REVIEW reviewed-for="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" reviewed-at="2026-09-13T07:52:40.925055+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

외부 내비가 연결되어 있으면 외부 내비만 사용하며, 현재 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 연결 종료 또는 수신 시간 초과가 확인되면 순정 내비를 각 설정에 따라 다시 사용합니다.

켜면 지원 차량의 순정 내비가 확인한 30km/h 구역에서 목표속도 상한을 적용하며, 끄면 이 구역 제한을 사용하지 않습니다. 일반 30km/h 구역에도 적용될 수 있으며 PV5는 지원하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 내비 연결 상태와 화면의 이벤트 종류·남은 거리를 함께 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:SETTING:END VehicleNaviSchoolZoneControl -->
