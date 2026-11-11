<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_BASIC" param="ClusterNaviMapTheme" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 클러스터 내비 지도 테마(1)

**메뉴:** 화면 표시 \> 외부 HUD \> 기본

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapTheme -->
<a id="ClusterNaviMapTheme"></a>

## 클러스터 내비 지도 테마(1)

`ClusterNaviMapTheme`

0: 자동 1: 다크 2: 라이트 변경하면 외부 내비가 자동으로 다시 연결됩니다.

<!-- CARROT:AUTO:BEGIN ClusterNaviMapTheme -->
<!-- CARROT:AUTO:SOURCE facts="07723b2fba065791dbe95aec7e30b282ff89d421fb2e93c18f8068044a77f77d" semantic="22c25adc7668b0b1e6f02c8676e96b5d9f45276bc7802f5e0fdc596b6f12bb21" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 다크 (`1`)
- **범위:** 자동 (`0`) ~ 라이트 (`2`)
- **변경 단위:** `1`
- **선택지:** `0` 자동, `1` 다크, `2` 라이트
- **메뉴:** 화면 표시 \> 외부 HUD \> 기본
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapTheme -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapTheme -->
<!-- CARROT:REVIEW reviewed-for="87294e7f3ad7b929ada06c18c8a6c0c4690b9fd5ce3b8f3faf54c31dffd43ba4" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 자동
- `1` — 다크
- `2` — 라이트 / 변경하면 외부 내비가 자동으로 다시 연결됩니다
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
<!-- CARROT:MANUAL:END ClusterNaviMapTheme -->

<!-- CARROT:SETTING:END ClusterNaviMapTheme -->
