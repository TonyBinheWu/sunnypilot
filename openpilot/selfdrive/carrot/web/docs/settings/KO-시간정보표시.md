<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_SCREEN" param="ShowDateTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 시간정보표시

**메뉴:** 화면 표시 \> 정보 표시

---

<!-- CARROT:SETTING:BEGIN ShowDateTime -->
<a id="ShowDateTime"></a>

## 시간정보표시

`ShowDateTime`

0:표시안함 1:시간+날짜 2:시간 3:날짜

<!-- CARROT:AUTO:BEGIN ShowDateTime -->
<!-- CARROT:AUTO:SOURCE facts="2a576cd03406d5a48fcf68a4fb3c4cf8df8205fde8eb62efa0a886700302bd6a" semantic="8a8a68471ac48ff4050425e0bbfaa30b75d9672c261cc13c269e729cc3d39c41" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `1`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 정보 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowDateTime -->

<!-- CARROT:MANUAL:BEGIN ShowDateTime -->
<!-- CARROT:REVIEW reviewed-for="8a8a68471ac48ff4050425e0bbfaa30b75d9672c261cc13c269e729cc3d39c41" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 표시안함
- `1` — 시간+날짜
- `2` — 시간
- `3` — 날짜
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 정보의 위치와 가독성을 확인하고, 필요한 정보만 표시되도록 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowDateTime -->

<!-- CARROT:SETTING:END ShowDateTime -->
