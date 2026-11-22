<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 우회전 안내 거리(m)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## 우회전 안내 거리(m)

`AutoTurnControlRightLaneChange`

지원되는 방향지시등 어댑터에서 우회전·우측 분기 안내를 준비하는 거리입니다. 0m는 끔, 최대 500m이며 ATC 1·2와 자동 깜빡이 모드 2에서 사용합니다. 화면 안내 후 실제 차로 변경은 운전자가 요청합니다.

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="05dbaa25a3b0a13c3c0654656d3f3ced8e08ae3dc9a421dbcb50a96af0b7be3f" semantic="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `500`
- **변경 단위:** `50`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

지원되는 방향지시등 어댑터에서 우회전·우측 분기 안내를 준비하는 거리입니다. 0m는 끔, 최대 500m이며 ATC 1·2와 자동 깜빡이 모드 2에서 사용합니다. 화면 안내 후 실제 차로 변경은 운전자가 요청합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
