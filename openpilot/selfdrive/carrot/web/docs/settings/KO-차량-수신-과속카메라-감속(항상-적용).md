<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleSpeedCameraControlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차량 수신 과속카메라 감속(항상 적용)

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraControlMode -->
<a id="VehicleSpeedCameraControlMode"></a>

## 차량 수신 과속카메라 감속(항상 적용)

`VehicleSpeedCameraControlMode`

외부 내비가 연결되지 않았을 때만 적용합니다. 외부 내비 연결 중에는 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 차량 CAN에서 수신한 과속카메라 단속속도를 자동 감속에 적용하는 방식을 선택합니다. Carrot Navi에서 수신하는 과속카메라 정보에는 영향을 주지 않습니다. 0: 사용 안 함 1: 가속페달과 관계없이 항상 적용 2: 차량 수신 카메라 감속이 시작된 뒤 새로 가속페달을 밟으면 현재 이벤트를 무시하는 것으로 보고, 감속구간에서 가속으로 도달한 최고속도를 감속 하한으로 유지 3: 가속페달을 밟는 동안 차량 수신 과속카메라 감속 해제

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:AUTO:SOURCE facts="055249507f5eeab3ce55ee3d934cdaedb528cd81b771085416b40593c77e885c" semantic="751d90cd219472ee82418f090d5685fd521295720a7ff37eb36bf0b66f9d92e9" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 항상 적용 (`1`)
- **범위:** 사용 안 함 (`0`) ~ 가속페달 입력 중 해제 (`3`)
- **변경 단위:** `1`
- **선택지:** `0` 사용 안 함, `1` 항상 적용, `2` 가속페달 감속 무시, `3` 가속페달 입력 중 해제
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraControlMode -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:REVIEW reviewed-for="9b48b9341a4ad5213f5220c933fa0f581110bf68f4e799917977eb831c1e67bd" reviewed-at="2026-09-13T07:52:40.930069+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

외부 내비가 연결되어 있으면 외부 내비만 사용하며, 현재 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 연결 종료 또는 수신 시간 초과가 확인되면 순정 내비를 각 설정에 따라 다시 사용합니다.

0은 사용 안 함, 1은 가속페달과 관계없이 적용, 2는 감속 시작 후 새 가속페달 입력으로 도달한 최고속도를 이벤트 종료까지 하한으로 유지, 3은 가속페달을 밟는 동안 해제합니다. 외부 내비 감속에는 이 모드를 적용하지 않습니다.

Kia PV5는 순정 내비의 같은 단속 상태·제한속도가 계속 수신되는 동안 짧은 알림이 꺼져도 연결된 카메라 거리를 유지합니다. 단속 상태 종료, 제한속도 변경 또는 두 내비 메시지 중 하나가 1초 넘게 유실되면 현재·대기 카메라 거리를 모두 해제합니다.

현재 카메라의 남은 거리가 끝나도 대기 거리만으로 다음 감속을 시작하지 않습니다. 새 유효 안내에 새로 받은 거리 정보가 연결되지 않으면 아래 가상거리를 사용하며, 완료된 카메라의 같은 안내로 다시 시작하지 않습니다. PV5의 경로 이탈을 독립적으로 검출하지는 않으며, 순정 내비가 단속 상태를 종료하거나 변경해야 해제됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 내비 연결 상태와 화면의 이벤트 종류·남은 거리를 함께 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraControlMode -->

<!-- CARROT:SETTING:END VehicleSpeedCameraControlMode -->
