<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: AutoTurnControl(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC: AutoTurnControl(0)

`AutoTurnControl`

0:사용안함 1:차선변경·턴 2:차선변경·턴+속도 3:속도 우회전 전 자동 차선변경 거리는 세부 설정에서 조정합니다. 0m는 끄기입니다. 추가 기능은 1·2번에서만 작동합니다.

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="f3a8a67a911690494be79e9e0b046b4346d4b8086ea1221974ce23bdcc281b70" semantic="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" reviewed-at="2026-11-02T22:15:29.530632+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

0은 끄기, 1은 차선변경·턴, 2는 차선변경·턴과 속도 제어, 3은 속도 제어입니다. 우회전 거리 추가 기능은 1·2번에서 설정 거리 안의 우측 깜박이를 요청합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

ATC 세부 설정에서 우회전 자동 차선변경 거리를 선택합니다. 거리를 높이면 더 앞에서 조건을 확인하고, 낮추면 턴에 가까워진 뒤 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

재시작 시 이전 4번은 1번으로 전환합니다. 별도 거리 설정이 없으면 250m를 사용하며 기존 명시 값은 보존합니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
