<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_PATH" param="CarrotTireTrajectory" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 타이어 궤적

**메뉴:** 화면 표시 \> 경로 표시

---

<!-- CARROT:SETTING:BEGIN CarrotTireTrajectory -->
<a id="CarrotTireTrajectory"></a>

## 타이어 궤적

`CarrotTireTrajectory`

차선 이탈 정도를 타이어 경로에 그라데이션(초록→빨강)으로 표시하고 하단에 편차(L/R/C, m)를 함께 표시합니다. 0:끄기, 1:켜기

<!-- CARROT:AUTO:BEGIN CarrotTireTrajectory -->
<!-- CARROT:AUTO:SOURCE facts="9012f6ee7e1f37f11d9ab07e691cdcd53b91ee157ebf5b82af5ca1bfa3a54f90" semantic="5a96ee68d440c85103f4c4ff1d0ac55cc74ac347d5e3536e424bbf25810c2a34" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 화면 표시 \> 경로 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotTireTrajectory -->

<!-- CARROT:MANUAL:BEGIN CarrotTireTrajectory -->
<!-- CARROT:REVIEW reviewed-for="5a96ee68d440c85103f4c4ff1d0ac55cc74ac347d5e3536e424bbf25810c2a34" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 끄기
- `1` — 켜기
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 크루즈·레인모드 상태를 바꿔 보며 경로 모양과 색상이 의도대로 전환되는지 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CarrotTireTrajectory -->

<!-- CARROT:SETTING:END CarrotTireTrajectory -->
