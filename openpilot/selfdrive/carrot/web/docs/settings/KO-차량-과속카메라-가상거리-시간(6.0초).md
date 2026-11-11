<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleSpeedCameraDistanceTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차량 과속카메라 가상거리 시간(6.0초)

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraDistanceTime -->
<a id="VehicleSpeedCameraDistanceTime"></a>

## 차량 과속카메라 가상거리 시간(6.0초)

`VehicleSpeedCameraDistanceTime`

외부 내비가 연결되지 않았을 때만 적용합니다. 외부 내비 연결 중에는 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 차량이 과속카메라 거리 없이 단속속도만 보낼 때 가상 감속거리를 만듭니다. 저장값은 0.1초 단위이며 60은 6.0초, 62는 6.2초입니다. 가상거리(m) = 단속속도(km/h) × 설정시간(초)으로 계산하므로 50 km/h에서 62는 310 m입니다. 설정값이 작을수록 가상거리가 짧아져 감속을 더 일찍 또는 더 강하게 시작할 수 있습니다. 변경값은 주행 중 약 1초 이내에 적용됩니다. 지원 CAN-FD 차량에서 현재 경고와 일치하는 가까운 거리가 없을 때도 적용합니다. 새 경고나 제한속도 변경 시 다시 시작하며, 거리가 소진되어도 경고가 유지되는 동안에는 감속 제한을 유지하고 가상거리를 반복 연장하지 않습니다.

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:AUTO:SOURCE facts="080d1ab05711270bbffa1233dcdda075d510aef70fd3ea3dda3f90c1d172a17b" semantic="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `60`
- **범위:** `10` ~ `200`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:REVIEW reviewed-for="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" reviewed-at="2026-09-13T09:14:59.497659+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

외부 내비가 연결되어 있으면 외부 내비만 사용하며, 현재 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 연결 종료 또는 수신 시간 초과가 확인되면 순정 내비를 각 설정에 따라 다시 사용합니다.

차량이 단속속도만 보내고 거리를 보내지 않을 때 가상거리를 계산합니다. 값을 높이면 가상거리가 길어지고, 낮추면 짧아져 더 일찍 또는 강하게 감속할 수 있습니다.
지원 CAN-FD 차량에서 현재 경고와 일치하는 가까운 거리가 없을 때도 사용합니다. 새 경고나 제한속도 변경 시 거리를 새로 시작하고 주행거리만큼 줄입니다. 거리가 소진되어도 경고가 유지되는 동안에는 감속 제한을 유지하며 가상거리를 반복해서 늘리지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 내비 연결 상태와 화면의 이벤트 종류·남은 거리를 함께 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:SETTING:END VehicleSpeedCameraDistanceTime -->
