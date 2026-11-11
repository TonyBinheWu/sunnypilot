<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviDecelCancelMobileZone" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 감속 중지: 이동식 단속 구간

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelMobileZone -->
<a id="VehicleNaviDecelCancelMobileZone"></a>

## 감속 중지: 이동식 단속 구간

`VehicleNaviDecelCancelMobileZone`

감속 중지 요청이 켜져 있을 때, 이동식 단속 구간(내비 파란 원)의 감속을 + 버튼·악셀톡으로 중지할 수 있게 합니다. 네비게이션감속모드(AutoNaviSpeedCtrlMode)가 3일 때만 이동식 구간에서 감속하므로, 모드 2 이하에서는 쓰이지 않습니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:AUTO:SOURCE facts="8a2082774198bddf51e858e15535aab29c003e0fd1304061161b8f08eb8bfdcc" semantic="570b00e282ceb2973c52e7d7121aea5fd059e453aac9b714b972da032891c62e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `1`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:REVIEW reviewed-for="570b00e282ceb2973c52e7d7121aea5fd059e453aac9b714b972da032891c62e" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

상위 감속 중지 요청이 켜진 상태에서 이 항목을 켜면 이동식 단속 구간 감속을 + 또는 악셀톡으로 중지할 수 있습니다. 끄면 해당 종류의 중지를 허용하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

이동식 구간 자체의 감속은 내비게이션 감속 모드 3에서만 동작합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelMobileZone -->
