<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_RADAR" param="ClusterHudRadarSourceColor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 레이더 소스 색구분(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 레이더 표시

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarSourceColor -->
<a id="ClusterHudRadarSourceColor"></a>

## 외부 HUD 레이더 소스 색구분(0)

`ClusterHudRadarSourceColor`

0: 기본(모든 차량 회색) 1: 켜짐(SCC=R, HDA=B, RADAR=O)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarSourceColor -->
<!-- CARROT:AUTO:SOURCE facts="00a32ad90b3fa801a7e48a88fe61cf6cd86df9381ffcd9da989959b650452b5e" semantic="e1a4577beb594b1aee54203a64b4d871bb2dcc847004a709ddfd411c1a3f15b9" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 화면 표시 \> 외부 HUD \> 레이더 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarSourceColor -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarSourceColor -->
<!-- CARROT:REVIEW reviewed-for="e1a4577beb594b1aee54203a64b4d871bb2dcc847004a709ddfd411c1a3f15b9" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 기본(모든 차량 회색)
- `1` — 켜짐(SCC=R, HDA=B, RADAR=O)
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD에서 같은 선행차와 주변 물체를 보며 표시 대상·거리·출처 구분을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarSourceColor -->

<!-- CARROT:SETTING:END ClusterHudRadarSourceColor -->
