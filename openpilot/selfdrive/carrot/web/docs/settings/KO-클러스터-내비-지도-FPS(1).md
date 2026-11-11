<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_BASIC" param="ClusterNaviMapFps" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 클러스터 내비 지도 FPS(1)

**메뉴:** 화면 표시 \> 외부 HUD \> 기본

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapFps -->
<a id="ClusterNaviMapFps"></a>

## 클러스터 내비 지도 FPS(1)

`ClusterNaviMapFps`

0: 5 FPS 1: 10 FPS(기본) 2: 20 FPS 3: 30 FPS HUD FPS와는 별개이며 지도 비트레이트는 자동 설정됩니다. 변경하면 외부 내비가 자동으로 다시 연결됩니다.

<!-- CARROT:AUTO:BEGIN ClusterNaviMapFps -->
<!-- CARROT:AUTO:SOURCE facts="1ed3207606cc12d0c16cb2bbbe1b996c1051e174c0e107924161046793dd04b4" semantic="e37c29337d96679ca12cd545db724e093fed073e51e81b87e087206f74a837b1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** 10 FPS (`1`)
- **범위:** 5 FPS (`0`) ~ 30 FPS (`3`)
- **변경 단위:** `1`
- **선택지:** `0` 5 FPS, `1` 10 FPS, `2` 20 FPS, `3` 30 FPS
- **메뉴:** 화면 표시 \> 외부 HUD \> 기본
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapFps -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapFps -->
<!-- CARROT:REVIEW reviewed-for="60a988eea43a59afc28a79f8db4eb165d0c12f35d06be7d5355a8d51c79c7451" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 5 FPS
- `1` — 10 FPS(기본)
- `2` — 20 FPS
- `3` — 30 FPS / HUD FPS와는 별개이며 지도 비트레이트는 자동 설정됩니다. / 변경하면 외부 내비가 자동으로 다시 연결됩니다
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD를 연결한 상태에서 변경하고, 화면 방향·밝기·지도 연결 상태를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 지도 FPS는 HUD 본 화면 FPS와 별개이며, 선택한 FPS에 맞춰 지도 비트레이트가 자동으로 정해집니다. 변경하면 외부 내비가 다시 연결됩니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ClusterNaviMapFps -->

<!-- CARROT:SETTING:END ClusterNaviMapFps -->
