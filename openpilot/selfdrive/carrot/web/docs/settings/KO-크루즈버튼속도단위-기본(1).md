<!-- CARROT:GENERATED schema="1" locale="ko" group="BUTTON_UNIT" param="CruiseSpeedUnitBasic" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 크루즈버튼속도단위 기본(1)

**메뉴:** 주행 제어 \> 버튼·프리셋 \> 속도 단위

---

<!-- CARROT:SETTING:BEGIN CruiseSpeedUnitBasic -->
<a id="CruiseSpeedUnitBasic"></a>

## 크루즈버튼속도단위 기본(1)

`CruiseSpeedUnitBasic`

크루즈버튼 속도조절 단위(기본단위)

<!-- CARROT:AUTO:BEGIN CruiseSpeedUnitBasic -->
<!-- CARROT:AUTO:SOURCE facts="f2a058ce8c5f8eb7ee98e2d54eedaae1e0947b2123c6c2f429c641b5f81f38a3" semantic="7b48bb82f966475975d3c3d2c777ca567eb1ed3846b4d9fa5f3ec085600de7a0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `10km/h`
- **범위:** `1km/h` ~ `100km/h`
- **변경 단위:** `1`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 버튼·프리셋 \> 속도 단위
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseSpeedUnitBasic -->

<!-- CARROT:MANUAL:BEGIN CruiseSpeedUnitBasic -->
<!-- CARROT:REVIEW reviewed-for="7b48bb82f966475975d3c3d2c777ca567eb1ed3846b4d9fa5f3ec085600de7a0" reviewed-at="2026-09-22T02:17:37+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

크루즈버튼 속도조절 단위(기본단위).

- **값을 높이면:** 기본 버튼 모드에서 한 번에 바뀌는 설정 속도 폭이 커집니다.
- **값을 낮추면:** 기본 조정 폭이 작아집니다.

폭스바겐의 일반 모드에서는 별도 +·-의 짧게 누르기에 적용합니다. SET은 현재 속도 설정, RES는 이전 설정속도 복원으로 처리합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

버튼을 한 번 누를 때와 길게 누를 때 설정 속도가 변하는 폭과 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseSpeedUnitBasic -->

<!-- CARROT:SETTING:END CruiseSpeedUnitBasic -->
