<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviDecelCancelBump" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 감속 중지: 과속방지턱

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelBump -->
<a id="VehicleNaviDecelCancelBump"></a>

## 감속 중지: 과속방지턱

`VehicleNaviDecelCancelBump`

감속 중지 요청이 켜져 있을 때, 순정 내비 과속방지턱 감속을 + 버튼·악셀톡으로 중지할 수 있게 합니다. 방지턱 감속 목표(AutoNaviSpeedBumpSpeed·AutoNaviSpeedBumpTime·AutoNaviSpeedDecelRate로 계산)가 설정 속도보다 낮아 실제로 감속 중일 때만 입력을 씁니다. 중지는 가장 가까운 방지턱 하나에만 적용됩니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:AUTO:SOURCE facts="df3174107262cf3a6ea62204e2a0ad0ebb5701860f67630a855e069341b70c70" semantic="ab15a94879c1067db343091913a6b8ee055f955c0564f0b44795d843826bedfd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `1`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelBump -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:REVIEW reviewed-for="ab15a94879c1067db343091913a6b8ee055f955c0564f0b44795d843826bedfd" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

상위 감속 중지 요청이 켜진 상태에서 이 항목을 켜면 가장 가까운 과속방지턱 하나 감속을 + 또는 악셀톡으로 중지할 수 있습니다. 끄면 해당 종류의 중지를 허용하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

계산된 방지턱 목표가 설정속도보다 낮아 실제 감속 중일 때만 입력을 사용합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelBump -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelBump -->
