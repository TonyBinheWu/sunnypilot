<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_RADAR" param="ClusterHudRadarDisplay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 레이더 표시 옵션(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 레이더 표시

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarDisplay -->
<a id="ClusterHudRadarDisplay"></a>

## 외부 HUD 레이더 표시 옵션(0)

`ClusterHudRadarDisplay`

0: 기본(가까운 레이더 포인트 병합) 1: 상세(레이더 포인트 병합 안함)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarDisplay -->
<!-- CARROT:AUTO:SOURCE facts="f51e48354baf70f7c3098808476513a53a971674bccfad11ce7b6355185efc45" semantic="c0542f70ce7ff639693facf6fed2c23f3d14b8dd10885a9e546818549e5afdce" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 화면 표시 \> 외부 HUD \> 레이더 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarDisplay -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarDisplay -->
<!-- CARROT:REVIEW reviewed-for="c0542f70ce7ff639693facf6fed2c23f3d14b8dd10885a9e546818549e5afdce" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 기본(가까운 레이더 포인트 병합)
- `1` — 상세(레이더 포인트 병합 안함)
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD에서 같은 선행차와 주변 물체를 보며 표시 대상·거리·출처 구분을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarDisplay -->

<!-- CARROT:SETTING:END ClusterHudRadarDisplay -->
