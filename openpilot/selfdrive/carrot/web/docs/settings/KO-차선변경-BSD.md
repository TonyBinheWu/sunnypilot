<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="LaneChangeBsd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차선변경 BSD

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN LaneChangeBsd -->
<a id="LaneChangeBsd"></a>

## 차선변경 BSD

`LaneChangeBsd`

0: BSD검출(조향토크허용) 1: 조향토크불허 -1: BSD사용안함

<!-- CARROT:AUTO:BEGIN LaneChangeBsd -->
<!-- CARROT:AUTO:SOURCE facts="8efcf399132ae8f8c8fdde603d643f88bfc018c67b9cadbae7d40c3f4bcfbdf8" semantic="04954a5af52833d5de668494cc66d168955efdddb321270af7866ff7bd295569" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `-1` ~ `1`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeBsd -->

<!-- CARROT:MANUAL:BEGIN LaneChangeBsd -->
<!-- CARROT:REVIEW reviewed-for="04954a5af52833d5de668494cc66d168955efdddb321270af7866ff7bd295569" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — BSD검출(조향토크허용)
- `1` — 조향토크불허
- `-1` — BSD사용안함
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차선이 명확하고 주변 차량이 없는 구간에서 방향지시등 작동 후 대기·차선 확인·완료 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

BSD는 운전자의 사각지대와 뒤차 안전 확인을 대신하지 않습니다. 자세한 내용은 [[차로 변경 이해하기|Guide-Lane-Change]]를 참고하세요.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeBsd -->

<!-- CARROT:SETTING:END LaneChangeBsd -->
