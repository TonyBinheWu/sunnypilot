<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="AutoBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 깜박이 자동제어

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN AutoBlinkerControl -->
<a id="AutoBlinkerControl"></a>

## 깜박이 자동제어

`AutoBlinkerControl`

0 블루투스 원터치. 1은 5km/h 이하에서 블루투스 버튼으로 켠 신호를 회전 완료까지 유지합니다. 2는 지원되는 운전자 요청 기능도 허용합니다. 같은 버튼은 취소, 반대 버튼은 방향 전환이며 순정 레버가 우선합니다. 내비 경로는 화면·음성으로 안내합니다.

<!-- CARROT:AUTO:BEGIN AutoBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="70c2d56822d1b0325bb554cfe5a3cc82f7ee43792c73bccc6e93dcb4abbed01f" semantic="6a1867189f6b090ec92c031c906f21c613b4aa48685d0feccb1587057093bf19" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN AutoBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="6a1867189f6b090ec92c031c906f21c613b4aa48685d0feccb1587057093bf19" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

0 블루투스 원터치. 1은 5km/h 이하에서 블루투스 버튼으로 켠 신호를 회전 완료까지 유지합니다. 2는 지원되는 운전자 요청 기능도 허용합니다. 같은 버튼은 취소, 반대 버튼은 방향 전환이며 순정 레버가 우선합니다. 내비 경로는 화면·음성으로 안내합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoBlinkerControl -->

<!-- CARROT:SETTING:END AutoBlinkerControl -->
