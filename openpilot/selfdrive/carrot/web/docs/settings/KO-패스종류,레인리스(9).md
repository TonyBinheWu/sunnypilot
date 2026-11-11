<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_PATH" param="ShowPathMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 패스종류,레인리스(9)

**메뉴:** 화면 표시 \> 경로 표시

---

<!-- CARROT:SETTING:BEGIN ShowPathMode -->
<a id="ShowPathMode"></a>

## 패스종류,레인리스(9)

`ShowPathMode`

0:일반,1,2:사각,3,4:^^,5,6:사각,7,8:^^,9,10,11:smooth^^,12:smooth2^^,13:3줄,14:2줄,15:1줄

<!-- CARROT:AUTO:BEGIN ShowPathMode -->
<!-- CARROT:AUTO:SOURCE facts="f0830439eaf5c7cf76fd4c49ea18dd503e638cc01014a26464f91ba2c83736dd" semantic="d31a5fd649594fe0f0ac8dc0f4999b3002731d1ad199cfccd1b0230368c0bd76" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** `9`
- **범위:** `0` ~ `15`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 경로 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathMode -->

<!-- CARROT:MANUAL:BEGIN ShowPathMode -->
<!-- CARROT:REVIEW reviewed-for="d31a5fd649594fe0f0ac8dc0f4999b3002731d1ad199cfccd1b0230368c0bd76" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 순정 경로 모양을 사용합니다.
- `1`~`8` — 사각형과 화살표 계열의 애니메이션 경로를 사용합니다.
- `9`~`12` — 부드러운 화살표 계열 경로를 사용합니다.
- `13`, `14`, `15` — 각각 3줄, 2줄, 1줄 경로를 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 크루즈·레인모드 상태를 바꿔 보며 경로 모양과 색상이 의도대로 전환되는지 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathMode -->

<!-- CARROT:SETTING:END ShowPathMode -->
