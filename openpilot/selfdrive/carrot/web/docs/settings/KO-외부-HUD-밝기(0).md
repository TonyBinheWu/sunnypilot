<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_BASIC" param="ClusterHudBrightness" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 밝기(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 기본

---

<!-- CARROT:SETTING:BEGIN ClusterHudBrightness -->
<a id="ClusterHudBrightness"></a>

## 외부 HUD 밝기(0)

`ClusterHudBrightness`

0: 자동 1~100: 밝기

<!-- CARROT:AUTO:BEGIN ClusterHudBrightness -->
<!-- CARROT:AUTO:SOURCE facts="e413c595da8148d1f541449ec11753a0311585b37a937aca8a5f2f5fe1982558" semantic="22a87e6cddc1752b7b1eeb6748de1b1b2c63a65f6e171b170e1ca2b1f17a1ece" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0%`
- **범위:** `0%` ~ `100%`
- **변경 단위:** `1`
- **표시 단위:** `%`
- **메뉴:** 화면 표시 \> 외부 HUD \> 기본
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudBrightness -->

<!-- CARROT:MANUAL:BEGIN ClusterHudBrightness -->
<!-- CARROT:REVIEW reviewed-for="22a87e6cddc1752b7b1eeb6748de1b1b2c63a65f6e171b170e1ca2b1f17a1ece" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 자동 밝기를 사용합니다. 연결된 주 화면 밝기를 사용할 수 없으면 외부 HUD 기본 밝기를 사용합니다.
- `1`~`100` — 외부 HUD 밝기를 해당 백분율로 고정합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD를 연결한 상태에서 변경하고, 화면 방향·밝기·지도 연결 상태를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudBrightness -->

<!-- CARROT:SETTING:END ClusterHudBrightness -->
