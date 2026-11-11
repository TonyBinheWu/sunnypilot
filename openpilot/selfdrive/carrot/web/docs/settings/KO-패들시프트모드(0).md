<!-- CARROT:GENERATED schema="1" locale="ko" group="BUTTON_MODE" param="PaddleMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 패들시프트모드(0)

**메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드

---

<!-- CARROT:SETTING:BEGIN PaddleMode -->
<a id="PaddleMode"></a>

## 패들시프트모드(0)

`PaddleMode`

0:크루즈ON, 1:크루즈대기, 2:자동감속, 3:CarrotCruise

<!-- CARROT:AUTO:BEGIN PaddleMode -->
<!-- CARROT:AUTO:SOURCE facts="ee87e875ac1514c9e901cdbc2c69f72f2eb4c24509da17e471239a8102aa0e50" semantic="513264e6a1d57186ce13925ba169f9b25c61b0d5d02385d078e00fd84cb40d9d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `1`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END PaddleMode -->

<!-- CARROT:MANUAL:BEGIN PaddleMode -->
<!-- CARROT:REVIEW reviewed-for="513264e6a1d57186ce13925ba169f9b25c61b0d5d02385d078e00fd84cb40d9d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 크루즈ON
- `1` — 크루즈대기
- `2` — 자동감속
- `3` — CarrotCruise
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

정차 상태에서 모드를 선택한 뒤 짧게 누르기·길게 누르기·취소 동작을 각각 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END PaddleMode -->

<!-- CARROT:SETTING:END PaddleMode -->
