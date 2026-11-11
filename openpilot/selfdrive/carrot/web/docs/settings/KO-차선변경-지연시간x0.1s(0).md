<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="LaneChangeDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차선변경 지연시간x0.1s(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN LaneChangeDelay -->
<a id="LaneChangeDelay"></a>

## 차선변경 지연시간x0.1s(0)

`LaneChangeDelay`

방향지시등을 켜고 설정시간 후 차선변경합니다.

<!-- CARROT:AUTO:BEGIN LaneChangeDelay -->
<!-- CARROT:AUTO:SOURCE facts="2ae517026e726f0f44294702ff17c7f72ced26663dbbb1d3c8ebf65da4fdb244" semantic="6740c9942977f73420ed5c963b1d5773b4d958e0c8fb4bb8e03d397a45348792" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `100`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeDelay -->

<!-- CARROT:MANUAL:BEGIN LaneChangeDelay -->
<!-- CARROT:REVIEW reviewed-for="6740c9942977f73420ed5c963b1d5773b4d958e0c8fb4bb8e03d397a45348792" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

방향지시등을 켜고 설정시간 후 차선변경합니다.

- **값을 높이면:** 적용 시간 또는 지연 기준이 길어집니다.
- **값을 낮추면:** 적용 시간 또는 지연 기준이 짧아집니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차선이 명확하고 주변 차량이 없는 구간에서 방향지시등 작동 후 대기·차선 확인·완료 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

이 설정이 바꾸는 것은 진입 전 대기시간이며 진행 중 차로 변경 속도가 아닙니다. 자세한 내용은 [[차로 변경 이해하기|Guide-Lane-Change]]를 참고하세요.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeDelay -->

<!-- CARROT:SETTING:END LaneChangeDelay -->
