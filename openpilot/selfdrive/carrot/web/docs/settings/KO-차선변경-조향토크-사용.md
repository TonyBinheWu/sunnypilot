<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="LaneChangeNeedTorque" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차선변경 조향토크 사용

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN LaneChangeNeedTorque -->
<a id="LaneChangeNeedTorque"></a>

## 차선변경 조향토크 사용

`LaneChangeNeedTorque`

-1:자동차선변경사용안함 0: 즉시 차선변경 1: 토크필요

<!-- CARROT:AUTO:BEGIN LaneChangeNeedTorque -->
<!-- CARROT:AUTO:SOURCE facts="2aadb92b82e5d2a55f15bd21415c700f83dab5b98d02409fa206c32e8181cfd2" semantic="70cb75233be32678e1cf5e9957be1e809887dca4e08053751f65ac6a2f29c189" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `-1` ~ `1`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeNeedTorque -->

<!-- CARROT:MANUAL:BEGIN LaneChangeNeedTorque -->
<!-- CARROT:REVIEW reviewed-for="70cb75233be32678e1cf5e9957be1e809887dca4e08053751f65ac6a2f29c189" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `-1` — 자동차선변경사용안함
- `0` — 즉시 차선변경
- `1` — 토크필요
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차선이 명확하고 주변 차량이 없는 구간에서 방향지시등 작동 후 대기·차선 확인·완료 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

차로 변경 경로를 누가 결정하는지와 안전 확인 책임은 [[차로 변경 이해하기|Guide-Lane-Change]]를 참고하세요.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeNeedTorque -->

<!-- CARROT:SETTING:END LaneChangeNeedTorque -->
