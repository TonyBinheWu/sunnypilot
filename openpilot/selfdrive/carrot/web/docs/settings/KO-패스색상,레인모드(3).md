<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_PATH" param="ShowPathColorLane" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 패스색상,레인모드(3)

**메뉴:** 화면 표시 \> 경로 표시

---

<!-- CARROT:SETTING:BEGIN ShowPathColorLane -->
<a id="ShowPathColorLane"></a>

## 패스색상,레인모드(3)

`ShowPathColorLane`

(+10:띠)0:빨,1:주,2:노,3:초,4:파,5:남,6:보,7:고,8:흰,9:검,20:Auto

<!-- CARROT:AUTO:BEGIN ShowPathColorLane -->
<!-- CARROT:AUTO:SOURCE facts="9c0d8eadf1cdb03190e2a80ae8bf143b1c91086c64b4fadeee9082afbf17b085" semantic="d7455a9fd2a86afc0293993b98b72bc99a8a9c2a0375adef24f7a5d5888c9f38" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** `3`
- **범위:** `0` ~ `20`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 경로 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColorLane -->

<!-- CARROT:MANUAL:BEGIN ShowPathColorLane -->
<!-- CARROT:REVIEW reviewed-for="d7455a9fd2a86afc0293993b98b72bc99a8a9c2a0375adef24f7a5d5888c9f38" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

`0`~`9`는 빨강·주황·노랑·초록·파랑·남색·보라·갈색·흰색·검정 순으로 레인모드 경로 색을 선택합니다. `10`~`19`는 같은 색에 강조 외곽선을 추가하고, `20`은 주행 상태에 따라 색을 자동 선택합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 크루즈·레인모드 상태를 바꿔 보며 경로 모양과 색상이 의도대로 전환되는지 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColorLane -->

<!-- CARROT:SETTING:END ShowPathColorLane -->
