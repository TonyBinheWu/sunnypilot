<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="LaneChangeLeverWait" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 원터치 차선변경 요청 5회 대기

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN LaneChangeLeverWait -->
<a id="LaneChangeLeverWait"></a>

## 원터치 차선변경 요청 5회 대기

`LaneChangeLeverWait`

현대 CAN-FD(0x3C1 레버 신호) 전용. 레버를 원터치로 눌렀는데 차선변경이 바로 승인되지 않으면(BSD·옆 차량·차선 등 기존 판단), 누른 시점부터 깜빡이 5회(약 4초) 동안 깜빡이를 유지하며 기다립니다. 그 안에 풀리면 차선변경하고, 안 풀리면 요청을 포기하며 남은 깜빡임으로는 다시 시작하지 않습니다. 레버를 고정한 경우는 기존대로 계속 기다립니다.

<!-- CARROT:AUTO:BEGIN LaneChangeLeverWait -->
<!-- CARROT:AUTO:SOURCE facts="7f4552cbb499e705e9c82ce9c2c87d2b635759eb768e2d7a8c1dfb60f07673e6" semantic="ea223332818ad995bfa4b772614a0e20f4c64f676f70ec1be8afd5eb871ae2db" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeLeverWait -->

<!-- CARROT:MANUAL:BEGIN LaneChangeLeverWait -->
<!-- CARROT:REVIEW reviewed-for="ea223332818ad995bfa4b772614a0e20f4c64f676f70ec1be8afd5eb871ae2db" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 원터치 차선변경이 BSD·차선 등의 조건으로 막혔을 때 방향지시등과 요청을 약 4초 동안 유지합니다. 차선변경 지연 시간은 별도로 더하며, 시간이 지나면 요청을 버립니다. 끄면 기존 램프 기반 대기를 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

레버를 고정하면 시간제한 없이 기존 조건을 기다립니다. 대기가 끝난 뒤에는 새 조작으로 다시 요청합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END LaneChangeLeverWait -->

<!-- CARROT:SETTING:END LaneChangeLeverWait -->
