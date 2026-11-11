<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoTurnControlTurnEnd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: 시간거리(3)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlTurnEnd -->
<a id="AutoTurnControlTurnEnd"></a>

## ATC: 시간거리(3)

`AutoTurnControlTurnEnd`

NOO완료 시간거리(속도\*시간)

<!-- CARROT:AUTO:BEGIN AutoTurnControlTurnEnd -->
<!-- CARROT:AUTO:SOURCE facts="e4160e7ee41e7f1ea1954e34dcd38bf97b593c9fec0ca4c675a568ed1ccc5bb1" semantic="55ebb6f698365577e35dd91320b04f3f559583fa75f0b6bffd5f11af27bea89d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `6`
- **범위:** `0` ~ `30`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlTurnEnd -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlTurnEnd -->
<!-- CARROT:REVIEW reviewed-for="55ebb6f698365577e35dd91320b04f3f559583fa75f0b6bffd5f11af27bea89d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

NOO완료 시간거리(속도*시간).

- **값을 높이면:** 적용 시간 또는 지연 기준이 길어집니다.
- **값을 낮추면:** 적용 시간 또는 지연 기준이 짧아집니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차선이 명확하고 주변 차량이 없는 구간에서 방향지시등 작동 후 대기·차선 확인·완료 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoTurnControlTurnEnd -->

<!-- CARROT:SETTING:END AutoTurnControlTurnEnd -->
