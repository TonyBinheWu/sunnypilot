<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoTurnMapChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC Helper 맵전환(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoTurnMapChange -->
<a id="AutoTurnMapChange"></a>

## ATC Helper 맵전환(0)

`AutoTurnMapChange`

ATC 작동시 자동맵전환

<!-- CARROT:AUTO:BEGIN AutoTurnMapChange -->
<!-- CARROT:AUTO:SOURCE facts="7e5fa8700ca81ede020f21cb2ec6932542390ff893abb87a8b6eeecdb575ab62" semantic="e5a6acf262e3326cb0dab44709ee7c0a63122f628c93714fdb9143510beeead6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnMapChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnMapChange -->
<!-- CARROT:REVIEW reviewed-for="e5a6acf262e3326cb0dab44709ee7c0a63122f628c93714fdb9143510beeead6" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** ATC 턴 제어가 활성화되면 연결된 화면을 지도 모드로 전환하고, 구간을 벗어나면 도로 화면으로 되돌립니다.
- **꺼짐:** ATC가 화면 전환 명령을 보내지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차선이 명확하고 주변 차량이 없는 구간에서 방향지시등 작동 후 대기·차선 확인·완료 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> ATC가 작동할 때 연결된 외부 내비 지도 화면으로 전환하는 보조 기능입니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoTurnMapChange -->

<!-- CARROT:SETTING:END AutoTurnMapChange -->
