<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviDecelCancelBox" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 감속 중지: 박스형 카메라

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelBox -->
<a id="VehicleNaviDecelCancelBox"></a>

## 감속 중지: 박스형 카메라

`VehicleNaviDecelCancelBox`

감속 중지 요청이 켜져 있을 때, 순정 내비가 박스형(이동식 카메라 함, 예고 종류 2)으로 알린 카메라의 감속을 + 버튼·악셀톡으로 중지할 수 있게 합니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelBox -->
<!-- CARROT:AUTO:SOURCE facts="b7652d989d73c78bfe7c7405ed35719e40d947d957a6a7cfbf5219f79101439f" semantic="42f846ee76666e7420105b1833d0fa4ff8f300b9c3d5efc820cd0fdc3d3d1eef" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `1`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelBox -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelBox -->
<!-- CARROT:REVIEW reviewed-for="42f846ee76666e7420105b1833d0fa4ff8f300b9c3d5efc820cd0fdc3d3d1eef" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

상위 감속 중지 요청이 켜진 상태에서 이 항목을 켜면 박스형 단속 감속을 + 또는 악셀톡으로 중지할 수 있습니다. 끄면 해당 종류의 중지를 허용하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

고정식·신호·후면 단속 예고가 함께 확인되면 해당 단속의 감속을 유지합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelBox -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelBox -->
