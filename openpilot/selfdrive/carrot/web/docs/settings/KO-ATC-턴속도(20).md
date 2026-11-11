<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoTurnControlSpeedTurn" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: 턴속도(20)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlSpeedTurn -->
<a id="AutoTurnControlSpeedTurn"></a>

## ATC: 턴속도(20)

`AutoTurnControlSpeedTurn`

ATC 턴시 적용속도 0:사용안함

<!-- CARROT:AUTO:BEGIN AutoTurnControlSpeedTurn -->
<!-- CARROT:AUTO:SOURCE facts="b82b867e293d373914e76f2611697ef35b9f6a995bfed4ab449c39089eb05d75" semantic="faad48b2a790f2c99af8ac2842c96d8e3a430972367fdf5e0eb2fa6ebfc3f18f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `20km/h`
- **범위:** `0km/h` ~ `100km/h`
- **변경 단위:** `5`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlSpeedTurn -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlSpeedTurn -->
<!-- CARROT:REVIEW reviewed-for="faad48b2a790f2c99af8ac2842c96d8e3a430972367fdf5e0eb2fa6ebfc3f18f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

ATC 턴시 적용속도.

- **값을 높이면:** 적용되는 속도 또는 속도 기준이 높아집니다.
- **값을 낮추면:** 속도 또는 속도 기준이 낮아집니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차선이 명확하고 주변 차량이 없는 구간에서 방향지시등 작동 후 대기·차선 확인·완료 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0`은 ATC 턴 목표 속도를 사용하지 않습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoTurnControlSpeedTurn -->

<!-- CARROT:SETTING:END AutoTurnControlSpeedTurn -->
