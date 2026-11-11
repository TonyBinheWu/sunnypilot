<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_SCREEN" param="ShowLaneInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차선정보

**메뉴:** 화면 표시 \> 정보 표시

---

<!-- CARROT:SETTING:BEGIN ShowLaneInfo -->
<a id="ShowLaneInfo"></a>

## 차선정보

`ShowLaneInfo`

-1:없음 0:패스만 1:레인 2:로드엣지

<!-- CARROT:AUTO:BEGIN ShowLaneInfo -->
<!-- CARROT:AUTO:SOURCE facts="f0eed7ada2a60be0c9d9a7e215c2d533a8a1c5d4f33d6c8e04523645df8c6655" semantic="7c35ba7d1d497e19a704752026f79ad2d1e535149cf588d95bce85285926322b" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `1`
- **범위:** `-1` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 정보 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowLaneInfo -->

<!-- CARROT:MANUAL:BEGIN ShowLaneInfo -->
<!-- CARROT:REVIEW reviewed-for="7c35ba7d1d497e19a704752026f79ad2d1e535149cf588d95bce85285926322b" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `-1` — 없음
- `0` — 패스만
- `1` — 레인
- `2` — 로드엣지
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 정보의 위치와 가독성을 확인하고, 필요한 정보만 표시되도록 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowLaneInfo -->

<!-- CARROT:SETTING:END ShowLaneInfo -->
