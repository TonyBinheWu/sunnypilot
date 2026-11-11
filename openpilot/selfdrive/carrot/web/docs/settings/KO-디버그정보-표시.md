<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_SCREEN" param="ShowDebugUI" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 디버그정보 표시

**메뉴:** 화면 표시 \> 정보 표시

---

<!-- CARROT:SETTING:BEGIN ShowDebugUI -->
<a id="ShowDebugUI"></a>

## 디버그정보 표시

`ShowDebugUI`

디버그정보 표시

<!-- CARROT:AUTO:BEGIN ShowDebugUI -->
<!-- CARROT:AUTO:SOURCE facts="cc17ce8fab5c14f95108a0b6d572ab52ef2afd7df89861b99e09cdd861fb57e4" semantic="5427f7c6ad263c8644a81441bc61043f741eccdf5c7938a34fb92f7a0320090d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `1`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 정보 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowDebugUI -->

<!-- CARROT:MANUAL:BEGIN ShowDebugUI -->
<!-- CARROT:REVIEW reviewed-for="5427f7c6ad263c8644a81441bc61043f741eccdf5c7938a34fb92f7a0320090d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 디버그 정보를 숨깁니다.
- `1`, `2` — 현재 구현에서는 모두 주행 화면의 디버그 정보를 표시합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 정보의 위치와 가독성을 확인하고, 필요한 정보만 표시되도록 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowDebugUI -->

<!-- CARROT:SETTING:END ShowDebugUI -->
