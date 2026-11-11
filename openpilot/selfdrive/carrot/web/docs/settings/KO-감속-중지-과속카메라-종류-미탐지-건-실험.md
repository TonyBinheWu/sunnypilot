<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviDecelCancelUnknown" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 감속 중지: 과속카메라 종류 미탐지 건 \[실험\]

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelUnknown -->
<a id="VehicleNaviDecelCancelUnknown"></a>

## 감속 중지: 과속카메라 종류 미탐지 건 \[실험\]

`VehicleNaviDecelCancelUnknown`

감속 중지 요청이 켜져 있을 때, 순정 내비 단속 경고 중 카메라 종류 예고를 받지 못했거나 해석하지 못한 경고(CAN 미수신·미처리)의 감속을 + 버튼·악셀톡으로 중지할 수 있게 하는 실험 기능입니다. 종류를 모르는 경고라 예고 없이 오는 신호·과속 카메라도 포함될 수 있어 기본값은 꺼짐이며, 상위를 켜도 이 항목은 따로 켜야 동작합니다. 30km/h 이하 경고(어린이·노인보호구역 등)와 구간단속 중에는 적용하지 않습니다. 중지한 뒤 신호·후면·고정식 예고가 확인되면 그 종류의 규칙을 따릅니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:AUTO:SOURCE facts="ec03b941ea45973a554f58971e8c970f8708a98d7f2377db922de45c02a40c9f" semantic="bc790dfd91a22232bbc47f0077d136baa937beae69d660870e3b370ffa0052a7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:REVIEW reviewed-for="bc790dfd91a22232bbc47f0077d136baa937beae69d660870e3b370ffa0052a7" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

상위 감속 중지 요청이 켜진 상태에서 이 항목을 켜면 종류 예고가 없거나 해석되지 않은 단속 경고 감속을 + 또는 악셀톡으로 중지할 수 있습니다. 끄면 해당 종류의 중지를 허용하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

종류 미탐지는 실제 단속도 포함할 수 있는 실험 옵션입니다. 30km/h 이하 경고와 구간단속에는 적용하지 않습니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelUnknown -->
