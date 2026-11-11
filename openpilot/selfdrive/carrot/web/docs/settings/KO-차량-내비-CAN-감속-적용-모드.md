<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviCanControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차량 내비 CAN 감속 적용 모드

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviCanControl -->
<a id="VehicleNaviCanControl"></a>

## 차량 내비 CAN 감속 적용 모드

`VehicleNaviCanControl`

외부 내비가 연결되지 않았을 때만 적용합니다. 외부 내비 연결 중에는 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 차량 순정 내비 CAN의 카메라·방지턱 실제 거리를 자동 감속에 사용하는 범위를 선택합니다. 경로 일치는 vNAVI의 현재 계산 경로와 미래 이벤트 경로가 같다는 뜻입니다. 0: 사용 안 함 1: 카메라·방지턱 항상 적용 2: 카메라는 항상, 방지턱은 경로 일치 시 적용 3: 카메라·방지턱 모두 경로 일치 시 적용 경로 정보가 2초 넘게 갱신되지 않으면 경로 없음으로 처리합니다. 차량이 현재 카메라 상태를 직접 확인한 감속은 VehicleSpeedCameraControlMode가 별도로 제어합니다. PV5의 직접 확인된 구간단속 상태는 1~3에서 유지됩니다. 실험 기능이므로 검증된 차량에서만 사용하세요. 현재 카메라 경고에는 같은 제한속도의 가까운 거리 후보만 연결하며, 같은 속도의 먼 카메라만 있으면 현재 경고의 가상거리를 사용합니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviCanControl -->
<!-- CARROT:AUTO:SOURCE facts="145a39171ca2523054d47c3aa8a11b46fe5376223427db2445948cdd6583fbbb" semantic="f8d1712821a73e6fe7eba60cf61124d25e39d1cbafcd0c3129f9732ab42f4b13" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 사용 안 함 (`0`)
- **범위:** 사용 안 함 (`0`) ~ 카메라·방지턱 경로 (`3`)
- **변경 단위:** `1`
- **선택지:** `0` 사용 안 함, `1` 카메라·방지턱 항상, `2` 카메라 항상·방지턱 경로, `3` 카메라·방지턱 경로
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviCanControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviCanControl -->
<!-- CARROT:REVIEW reviewed-for="9598e2a6ce6b00dcd5e8a0f1feae8f420e87990f1a27edc0aa0a46bbff15d34b" reviewed-at="2026-09-13T09:14:59.502659+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

외부 내비가 연결되어 있으면 외부 내비만 사용하며, 현재 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 연결 종료 또는 수신 시간 초과가 확인되면 순정 내비를 각 설정에 따라 다시 사용합니다.

외부 내비 미연결 시 0은 사용 안 함, 1은 경로 안내와 관계없이 카메라·방지턱 적용, 2는 카메라 항상·방지턱 경로 일치 시 적용, 3은 둘 다 경로 일치 시 적용입니다. 현재 차량이 직접 확인한 카메라 상태는 차량 수신 과속카메라 감속 설정을 따릅니다.
현재 카메라 경고에는 같은 제한속도의 가까운 거리만 연결합니다. 같은 속도의 먼 카메라만 있으면 현재 경고의 가상거리를 사용하고, 먼 카메라는 이후 접근을 위한 후보로 보존합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 내비 연결 상태와 화면의 이벤트 종류·남은 거리를 함께 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviCanControl -->

<!-- CARROT:SETTING:END VehicleNaviCanControl -->
