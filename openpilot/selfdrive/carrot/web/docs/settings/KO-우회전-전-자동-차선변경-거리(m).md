<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 우회전 전 자동 차선변경 거리(m)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## 우회전 전 자동 차선변경 거리(m)

`AutoTurnControlRightLaneChange`

0m는 끄기이며 설정한 거리 안에서 조건을 확인합니다. 250m는 기존 동작과 같고 300~400m도 선택할 수 있습니다. 기존 켜짐 설정은 최초 재시작 시 250m로 전환합니다. 기존 ATC에 추가되는 기능입니다. ATC 1·2번에서 10km/h 이상이며 TBT 우회전·우측 분기까지 설정 거리 이내일 때 실제 턴 시작 전까지 우측 깜박이를 요청합니다. Ioniq 5 PE USB2CAN 구성, AutoBlinkerControl=2, LaneChangeNeedTorque=0이 필요합니다. 후방은 유효한 차량 BSD 경고만 확인하며 코너 거리는 사용하지 않습니다. 우측 차선 전방 차량은 현재 거리와 상대속도로 예측한 3초 뒤 거리가 모두 5m 이상이어야 합니다. 전방 레이더 오류·수신 지연 시 시작하지 않습니다. 요청 전 조향은 조건 확인을 다시 시작하며, 요청 후 운전자 조향·수동 개입은 취소합니다. 10~30km/h에서 시작한 신호는 끝날 때까지 표시 전용으로 유지합니다. 30km/h 이상에서 시작한 신호만 기존 차선변경 흐름으로 연결합니다. 우측 차선부터 로드에지까지 2.5m 이상 여유가 필요합니다.

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="2ce0eb39ba7fd3168a5d0e67859dd95f9e10600aba3cdee6ef0833c39a797e16" semantic="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `500`
- **변경 단위:** `50`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" reviewed-at="2026-11-02T22:15:29.542142+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

0m는 끄기이며 값을 높이면 우회전·우측 분기에 더 먼 거리부터 조건을 확인합니다. 250m는 기존 범위에 해당하며, 기존 켜짐 값은 재시작 시 250m로 전환합니다.

10km/h 이상에서 우측 차선·로드에지, 유효한 BSD와 현재 및 3초 예측 전방 거리를 확인합니다. 30km/h 미만에 시작한 신호는 표시 전용이고, 그 이상에서 시작한 신호는 기존 차선변경 판단으로 연결됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
