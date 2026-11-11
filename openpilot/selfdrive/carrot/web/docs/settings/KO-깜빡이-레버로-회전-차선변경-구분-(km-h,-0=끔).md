<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="BlinkerLatchedTurn" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 깜빡이 레버로 회전/차선변경 구분 (km/h, 0=끔)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN BlinkerLatchedTurn -->
<a id="BlinkerLatchedTurn"></a>

## 깜빡이 레버로 회전/차선변경 구분 (km/h, 0=끔)

`BlinkerLatchedTurn`

현대 CAN-FD(0x3C1 레버 신호) 전용. 0이면 끔. 설정 속도 이하에서는 반만 밀어(원터치) 깜빡이가 켜짐-꺼짐-켜짐을 본 뒤 끝까지 걸면(고정) 좌/우회전, 그냥 고정하거나 원터치만 하면 차선변경으로 정하고, 레버가 원터치 위치에 있는 동안은 차선변경을 시작하지 않습니다(고정도 걸리기 전 약 0.1초 그 위치를 지나감). 설정 속도를 넘으면 레버를 고정해도 차선변경만 합니다.

<!-- CARROT:AUTO:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:AUTO:SOURCE facts="d213c0926eece8509fa6bd8a5be72af8b60e3e345b697ed53c69419ac5e1ba59" semantic="76514ada656e4e01d74e337bcc01f3dc8948509aca88bc57278eade000b25502" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0km/h`
- **범위:** `0km/h` ~ `80km/h`
- **변경 단위:** `5`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END BlinkerLatchedTurn -->

<!-- CARROT:MANUAL:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:REVIEW reviewed-for="76514ada656e4e01d74e337bcc01f3dc8948509aca88bc57278eade000b25502" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

설정 속도 이하에서 원터치 후 램프가 켜짐·꺼짐·다시 켜짐을 거친 뒤 레버를 고정하면 회전으로 판정합니다. 단순 고정이나 원터치는 차선변경이며, 값을 높이면 이 회전 조작을 사용할 속도 범위가 넓어집니다. 0은 기존 판정을 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

현대 CAN-FD 레버 신호 지원 차량에서 사용합니다. 설정 속도를 넘으면 같은 조작도 차선변경으로 처리합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END BlinkerLatchedTurn -->

<!-- CARROT:SETTING:END BlinkerLatchedTurn -->
