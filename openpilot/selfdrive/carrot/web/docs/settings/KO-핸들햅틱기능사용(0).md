<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_HYUNDAI" param="HapticFeedbackWhenSpeedCamera" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 핸들햅틱기능사용(0)

**메뉴:** 차량·하드웨어 \> 현대·기아

---

<!-- CARROT:SETTING:BEGIN HapticFeedbackWhenSpeedCamera -->
<a id="HapticFeedbackWhenSpeedCamera"></a>

## 핸들햅틱기능사용(0)

`HapticFeedbackWhenSpeedCamera`

0: 사용안함 1: 진동 2: 계기판 3: HUD표시

<!-- CARROT:AUTO:BEGIN HapticFeedbackWhenSpeedCamera -->
<!-- CARROT:AUTO:SOURCE facts="48cb6e1193a8c5a4822d39328bf9cab00bb8e39474b4828ab5421fca0faaa4d4" semantic="e9e7ad9d957bc03d8cb260062ab40a0f6d2de683d9c3d9106ea39f476072aad3" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> 현대·기아
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HapticFeedbackWhenSpeedCamera -->

<!-- CARROT:MANUAL:BEGIN HapticFeedbackWhenSpeedCamera -->
<!-- CARROT:REVIEW reviewed-for="e9e7ad9d957bc03d8cb260062ab40a0f6d2de683d9c3d9106ea39f476072aad3" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 사용안함
- `1` — 진동
- `2` — 계기판
- `3` — HUD표시
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량 사양과 배선 구성을 확인한 뒤 정차 상태에서 설정하고, 다음 주행에서 SCC·차선 경고 동작을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 차종·연식·HDA 세대·하네스 위치가 일치하지 않으면 SCC 또는 종방향 제어가 잘못 동작할 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HapticFeedbackWhenSpeedCamera -->

<!-- CARROT:SETTING:END HapticFeedbackWhenSpeedCamera -->
