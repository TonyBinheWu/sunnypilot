<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_RADAR" param="ClusterHudRadarInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 레이더 정보 표시(4)

**메뉴:** 화면 표시 \> 외부 HUD \> 레이더 표시

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarInfo -->
<a id="ClusterHudRadarInfo"></a>

## 외부 HUD 레이더 정보 표시(4)

`ClusterHudRadarInfo`

0: 표시 안함 1: 속도(차량만) 2: 속도,거리(차량만) 3: 속도(모두) 4: 속도,거리(모두)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarInfo -->
<!-- CARROT:AUTO:SOURCE facts="4a361e7317f949f45d5f7efc8d6d9249d11d09d2874a02e2b845231a7c540c4b" semantic="05cc3268420daab3de56e5bbd791d233fe6c5cccda542fd4688e6a5bd63dfa2a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** `4`
- **범위:** `0` ~ `4`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 외부 HUD \> 레이더 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarInfo -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarInfo -->
<!-- CARROT:REVIEW reviewed-for="05cc3268420daab3de56e5bbd791d233fe6c5cccda542fd4688e6a5bd63dfa2a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 표시 안함
- `1` — 속도(차량만)
- `2` — 속도,거리(차량만)
- `3` — 속도(모두)
- `4` — 속도,거리(모두)
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD에서 같은 선행차와 주변 물체를 보며 표시 대상·거리·출처 구분을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarInfo -->

<!-- CARROT:SETTING:END ClusterHudRadarInfo -->
