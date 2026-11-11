<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviDecelCancelEarlyWarning" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 감속 중지: 경고 조기 시작 보정 \[실험\]

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<a id="VehicleNaviDecelCancelEarlyWarning"></a>

## 감속 중지: 경고 조기 시작 보정 \[실험\]

`VehicleNaviDecelCancelEarlyWarning`

감속 중지 요청이 켜져 있을 때만 동작하는 실험 기능입니다. 순정 내비 단속 경고는 보통 카메라 앞 약 6.1m×제한속도(60km/h면 약 366m)에서 켜지는데, 일부 지역·차량에서는 이보다 일찍(60km/h에서 약 460m) 켜져 박스형·고정식·이동식 구간 예고와 짝을 찾지 못하고 '종류 미탐지'로 처리됩니다. 켜면 짝 찾기 범위의 앞쪽 끝을 최대 1.35배로 넓혀 이런 경고도 종류를 찾습니다. ⚠ 위험: 범위가 넓어진 만큼 근처의 이동식 카메라(이동식 단속 구간) 예고가 엉뚱한 경고에 붙을 수 있습니다. 이때 '감속 중지: 이동식 단속 구간'이 켜져 있거나 네비게이션감속모드(AutoNaviSpeedCtrlMode)가 2 이하(이동식 구간 무시)이면, 확률은 낮지만 실제 단속 카메라의 감속을 건너뛸 수 있습니다. 켜면 반드시 주행에서 동작을 확인하세요.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:AUTO:SOURCE facts="fe2383fe986ca7ad8f40fe570cd2c5c8c4b507b7123c20b7b18dfd49b772d8ba" semantic="ca6595f1bd5ba33a43b5c946ad4d3a7cb99440c06da4c111043f7d1654d3b7c6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:REVIEW reviewed-for="ca6595f1bd5ba33a43b5c946ad4d3a7cb99440c06da4c111043f7d1654d3b7c6" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

상위 감속 중지 요청과 함께 켜면 일찍 시작된 단속 경고의 종류를 찾는 범위를 넓힙니다. 끄면 기존 짝 찾기 범위를 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

실험 기능입니다. 인접한 이동식 예고를 잘못 연결하면 실제 단속 감속을 건너뛸 수 있으므로 종류 매칭이 잘못된 차량에서 켜짐·꺼짐 결과를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelEarlyWarning -->
