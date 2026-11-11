<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_PERF" param="ClusterHudDebug" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 디버깅(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 성능·디버그

---

<!-- CARROT:SETTING:BEGIN ClusterHudDebug -->
<a id="ClusterHudDebug"></a>

## 외부 HUD 디버깅(0)

`ClusterHudDebug`

0: 온로드에서만 1: 항상 2: 항상+UI 3: 항상+Navi

<!-- CARROT:AUTO:BEGIN ClusterHudDebug -->
<!-- CARROT:AUTO:SOURCE facts="48cdacfc5b862aa0f2ded3ce0c91af7656e4af6012b5de0cfed2d2e95b5c03f1" semantic="f3690826c5fa0e74264bedafa8192c8a74e880f3190c33ebf87d9b5748bcdf27" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 외부 HUD \> 성능·디버그
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudDebug -->

<!-- CARROT:MANUAL:BEGIN ClusterHudDebug -->
<!-- CARROT:REVIEW reviewed-for="f3690826c5fa0e74264bedafa8192c8a74e880f3190c33ebf87d9b5748bcdf27" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 온로드에서만
- `1` — 항상
- `2` — 항상+UI
- `3` — 항상+Navi
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

문제 진단 목적에서만 한 항목씩 변경하고, 외부 HUD의 프레임 유지와 시스템 부하를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudDebug -->

<!-- CARROT:SETTING:END ClusterHudDebug -->
