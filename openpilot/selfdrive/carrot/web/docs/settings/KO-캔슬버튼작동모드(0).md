<!-- CARROT:GENERATED schema="1" locale="ko" group="BUTTON_MODE" param="CancelButtonMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 캔슬버튼작동모드(0)

**메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드

---

<!-- CARROT:SETTING:BEGIN CancelButtonMode -->
<a id="CancelButtonMode"></a>

## 캔슬버튼작동모드(0)

`CancelButtonMode`

0:Long control, 1: Long + Lateral

<!-- CARROT:AUTO:BEGIN CancelButtonMode -->
<!-- CARROT:AUTO:SOURCE facts="4f3203374a9066f295341e3a7b9e20f9923e512024514ca3a29cbdc9f7aac3fa" semantic="3a5b61a8a0ff59fd0ac9cd4cb53b19b9c3f8b4e3a4a5aaae74449a4c4e87df04" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CancelButtonMode -->

<!-- CARROT:MANUAL:BEGIN CancelButtonMode -->
<!-- CARROT:REVIEW reviewed-for="3a5b61a8a0ff59fd0ac9cd4cb53b19b9c3f8b4e3a4a5aaae74449a4c4e87df04" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — Long control
- `1` — Long + Lateral
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

정차 상태에서 모드를 선택한 뒤 짧게 누르기·길게 누르기·취소 동작을 각각 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CancelButtonMode -->

<!-- CARROT:SETTING:END CancelButtonMode -->
