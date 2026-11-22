<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC 경로 안내 및 감속

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC 경로 안내 및 감속

`AutoTurnControl`

0 끔 · 1 경로 안내 · 2 경로 안내 및 감속 · 3 감속. 내비는 출구와 교차로를 안내합니다. 차로를 바꾸려면 운전자가 방향을 선택해야 합니다.

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="dad6ea86d73c0e0f413be901334a33cd8682d830949da969a4b293277f7d0521" semantic="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

0 끔 · 1 경로 안내 · 2 경로 안내 및 감속 · 3 감속. 내비는 출구와 교차로를 안내합니다. 차로를 바꾸려면 운전자가 방향을 선택해야 합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

교차로 안내는 1번, 안내와 감속은 2번, 감속만 사용하려면 3번을 선택하세요.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

차로를 바꾸려면 옆 차로를 확인한 뒤 해당 방향의 방향지시등을 켜세요.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
