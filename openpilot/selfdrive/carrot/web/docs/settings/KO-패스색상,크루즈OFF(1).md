<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_PATH" param="ShowPathColorCruiseOff" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 패스색상,크루즈OFF(1)

**메뉴:** 화면 표시 \> 경로 표시

---

<!-- CARROT:SETTING:BEGIN ShowPathColorCruiseOff -->
<a id="ShowPathColorCruiseOff"></a>

## 패스색상,크루즈OFF(1)

`ShowPathColorCruiseOff`

(+10:띠)0:빨,1:주,2:노,3:초,4:파,5:남,6:보,7:고,8:흰,9:검

<!-- CARROT:AUTO:BEGIN ShowPathColorCruiseOff -->
<!-- CARROT:AUTO:SOURCE facts="47e8a55d0f15c8bbda4e3ddcb1e961af7d7576d7c5055119fc6c920566d3ca96" semantic="a49ee2ac59951411b6a5ff92f21e37706f20d0ab78df06c01f21fdaff8b23119" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** `1`
- **범위:** `0` ~ `19`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 경로 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColorCruiseOff -->

<!-- CARROT:MANUAL:BEGIN ShowPathColorCruiseOff -->
<!-- CARROT:REVIEW reviewed-for="a49ee2ac59951411b6a5ff92f21e37706f20d0ab78df06c01f21fdaff8b23119" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

`0`~`9`는 빨강·주황·노랑·초록·파랑·남색·보라·갈색·흰색·검정 순으로 크루즈 비활성 경로 색을 선택합니다. `10`~`19`는 같은 색에 강조 외곽선을 추가합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 크루즈·레인모드 상태를 바꿔 보며 경로 모양과 색상이 의도대로 전환되는지 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColorCruiseOff -->

<!-- CARROT:SETTING:END ShowPathColorCruiseOff -->
