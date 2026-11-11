<!-- CARROT:GENERATED schema="1" locale="ko" group="BUTTON_MODE" param="LfaButtonMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LFA버튼작동모드(0)

**메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드

---

<!-- CARROT:SETTING:BEGIN LfaButtonMode -->
<a id="LfaButtonMode"></a>

## LFA버튼작동모드(0)

`LfaButtonMode`

0:일반 1:감속정지&Ready 2:당근크루즈

<!-- CARROT:AUTO:BEGIN LfaButtonMode -->
<!-- CARROT:AUTO:SOURCE facts="557b6ee8c7cb92b2ab0c94856ba1e1e32acbfdb89b9caa1ada8328ae1367c6b6" semantic="9c4b44838ae0dcff4397e38c706817d14778d81d616a5617a32fbc5b2d88e8ff" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LfaButtonMode -->

<!-- CARROT:MANUAL:BEGIN LfaButtonMode -->
<!-- CARROT:REVIEW reviewed-for="9c4b44838ae0dcff4397e38c706817d14778d81d616a5617a32fbc5b2d88e8ff" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 일반
- `1` — 감속정지&Ready
- `2` — 당근크루즈
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

정차 상태에서 모드를 선택한 뒤 짧게 누르기·길게 누르기·취소 동작을 각각 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LfaButtonMode -->

<!-- CARROT:SETTING:END LfaButtonMode -->
