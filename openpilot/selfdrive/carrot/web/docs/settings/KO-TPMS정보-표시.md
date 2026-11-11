<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_SCREEN" param="ShowTpms" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TPMS정보 표시

**메뉴:** 화면 표시 \> 정보 표시

---

<!-- CARROT:SETTING:BEGIN ShowTpms -->
<a id="ShowTpms"></a>

## TPMS정보 표시

`ShowTpms`

0:표시안함 1: 위 2: 아래 3: 둘다 ※ C4(MICI)는 해당 없음

<!-- CARROT:AUTO:BEGIN ShowTpms -->
<!-- CARROT:AUTO:SOURCE facts="63708f2c2c09ba1bd3c78d7f82201b2aeede7d67a5d73aa9a815c4b6986a5ace" semantic="fd79f1bf1968efdfc0592e51e5336d2ab76734d8ffd69c233cc4444a22b4c036" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `1`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 정보 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowTpms -->

<!-- CARROT:MANUAL:BEGIN ShowTpms -->
<!-- CARROT:REVIEW reviewed-for="8c41eb6b830837957be0bde4715e8c09993f67ca59b986365e08d8eab5ed8999" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 표시안함
- `1` — 위
- `2` — 아래
- `3` — 둘다
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 정보의 위치와 가독성을 확인하고, 필요한 정보만 표시되도록 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowTpms -->

<!-- CARROT:SETTING:END ShowTpms -->
