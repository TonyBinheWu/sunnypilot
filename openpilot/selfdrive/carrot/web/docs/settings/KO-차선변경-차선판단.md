<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="LaneLineCheck" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차선변경 차선판단

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN LaneLineCheck -->
<a id="LaneLineCheck"></a>

## 차선변경 차선판단

`LaneLineCheck`

0: 색상+타입(노란선차단) 1: 타입만(점선/실선) 2: 타입만+실선토크override

<!-- CARROT:AUTO:BEGIN LaneLineCheck -->
<!-- CARROT:AUTO:SOURCE facts="6eb68fc79d6bcf04c8b1cf4ae2d680e8d6eb3495b3b89305d10e01af6ee35488" semantic="5977a88be710cace4de2e0c770c5dc27e274c2c55f3693f68730b76f98956e5e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneLineCheck -->

<!-- CARROT:MANUAL:BEGIN LaneLineCheck -->
<!-- CARROT:REVIEW reviewed-for="5977a88be710cace4de2e0c770c5dc27e274c2c55f3693f68730b76f98956e5e" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 색상+타입(노란선차단)
- `1` — 타입만(점선/실선)
- `2` — 타입만+실선토크override
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차선이 명확하고 주변 차량이 없는 구간에서 방향지시등 작동 후 대기·차선 확인·완료 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

카메라나 차량이 차선을 잘못 분류할 수 있으며 실선 재정의는 통과를 안전하거나 합법적으로 만들지 않습니다. 자세한 내용은 [[차로 변경 이해하기|Guide-Lane-Change]]를 참고하세요.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneLineCheck -->

<!-- CARROT:SETTING:END LaneLineCheck -->
