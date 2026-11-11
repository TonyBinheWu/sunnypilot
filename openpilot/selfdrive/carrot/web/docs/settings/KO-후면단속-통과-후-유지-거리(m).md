<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="AutoNaviRearCameraHoldDistance" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 후면단속 통과 후 유지 거리(m)

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN AutoNaviRearCameraHoldDistance -->
<a id="AutoNaviRearCameraHoldDistance"></a>

## 후면단속 통과 후 유지 거리(m)

`AutoNaviRearCameraHoldDistance`

외부 내비가 후면 과속 또는 후면 신호·과속 카메라(TMAP 75/76)를 안내하면 카메라 지점을 지난 뒤 이 거리만큼 목표속도 제한을 유지합니다. 마지막 50m 접근에서 위치를 기억하며 안내가 사라지거나 다음 항목으로 바뀌어도 주행거리로 추적합니다. 단위는 m이며 0은 추가 유지를 끕니다. 값을 높이면 더 멀리까지 유지합니다. 정차 중에는 거리가 줄지 않습니다. 연결 종료·경로 이탈·내비 세션 변경 시 해제합니다. 순정 CAN의 후면 여부는 구분하지 못하므로 순정 경고에는 이 거리를 적용하지 않습니다. 카운트다운 종료는 속도 유지 종료와 다릅니다.

<!-- CARROT:AUTO:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:AUTO:SOURCE facts="b5c83e2282eb74e5fd4dcba9a8accb5aecfb7982e2191e82217a241c382819e1" semantic="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `100`
- **범위:** `0` ~ `300`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:MANUAL:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:REVIEW reviewed-for="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" reviewed-at="2026-09-13T09:14:59.601345+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

외부 내비가 후면 과속 또는 후면 신호·과속 카메라(TMAP 75/76)를 안내할 때 통과 후 목표속도 제한을 유지합니다. 높이면 더 멀리까지 유지하고 낮추면 더 빨리 해제하며, 0은 추가 유지를 끕니다.

마지막 50m 접근에서 위치를 기억한 뒤 주행거리로 추적합니다. 안내가 사라지거나 다음 항목으로 바뀌어도 유지하며 정차 중에는 거리를 차감하지 않습니다. 다른 감속 조건이 더 낮은 속도를 요구하면 그 조건을 적용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

표시·저장 단위는 m입니다. 카운트다운은 카메라 지점에서 끝나고 후면단속 유지 거리는 별도로 표시됩니다. 외부 연결 종료·경로 이탈·새 세션·주행거리 초기화·카메라 제어 비활성화 시 유지 상태를 초기화합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

순정 CAN은 후면 종류를 구분하지 못하므로 이 추가 거리를 적용하지 않습니다. 설정 거리는 실제 장비의 측정 종료를 보장하는 값이 아닙니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:SETTING:END AutoNaviRearCameraHoldDistance -->
