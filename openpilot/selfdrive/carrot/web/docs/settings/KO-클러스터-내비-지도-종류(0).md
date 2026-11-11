<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_BASIC" param="ClusterNaviMapType" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 클러스터 내비 지도 종류(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 기본

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapType -->
<a id="ClusterNaviMapType"></a>

## 클러스터 내비 지도 종류(0)

`ClusterNaviMapType`

0: 일반 지도 1: 위성 지도 변경하면 외부 내비가 자동으로 다시 연결됩니다.

<!-- CARROT:AUTO:BEGIN ClusterNaviMapType -->
<!-- CARROT:AUTO:SOURCE facts="37ff9e8accebad92fe73425ab040d83de05841ce2b0676201121480c32b9404c" semantic="74a31937ac7dd81fe72e06f0f41520736d6558235984d4865a8b22153b7a32f0" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 일반 지도 (`0`)
- **범위:** 일반 지도 (`0`) ~ 위성 지도 (`1`)
- **변경 단위:** `1`
- **선택지:** `0` 일반 지도, `1` 위성 지도
- **메뉴:** 화면 표시 \> 외부 HUD \> 기본
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapType -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapType -->
<!-- CARROT:REVIEW reviewed-for="cecc953658fa7976938bc4de62a707ed52b4d1c7a0755356e26cbb8c2f7e090e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 일반 지도
- `1` — 위성 지도 / 변경하면 외부 내비가 자동으로 다시 연결됩니다
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD를 연결한 상태에서 변경하고, 화면 방향·밝기·지도 연결 상태를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 변경하면 외부 내비 연결이 자동으로 다시 시작됩니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ClusterNaviMapType -->

<!-- CARROT:SETTING:END ClusterNaviMapType -->
