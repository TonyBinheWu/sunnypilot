<!-- CARROT:GENERATED schema="1" locale="ko" group="BUTTON_MODE" param="CruiseButtonMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 크루즈버튼작동모드(0)

**메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드

---

<!-- CARROT:SETTING:BEGIN CruiseButtonMode -->
<a id="CruiseButtonMode"></a>

## 크루즈버튼작동모드(0)

`CruiseButtonMode`

0:일반 1:사용자1 2:사용자2 3:사용자3(속도 테이블 사용)

<!-- CARROT:AUTO:BEGIN CruiseButtonMode -->
<!-- CARROT:AUTO:SOURCE facts="6a6d5ada9d52579c6f48d887b4d70df0f32a9733d20b1a9f6ead6afaf46d902f" semantic="f106c313d9301e43d396835fadab742302d3dc37007a00554bf7f574204238c1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonMode -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonMode -->
<!-- CARROT:REVIEW reviewed-for="f106c313d9301e43d396835fadab742302d3dc37007a00554bf7f574204238c1" reviewed-at="2026-09-22T02:17:37+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 일반
- `1` — 사용자1
- `2` — 사용자2
- `3` — 사용자3(속도 테이블 사용)

폭스바겐의 별도 SET은 현재 계기판 속도로 설정하고, RES는 브레이크 전 저장속도가 있으면 복원하며 없으면 기존 설정속도를 유지합니다. 초기 설정속도가 없으면 현재 속도를 사용합니다. 버튼 모드는 별도 +·-에 적용되며, 수동 인게이지는 기존처럼 물리 SET·RES를 놓을 때 요청합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

정차 상태에서 모드를 선택한 뒤 짧게 누르기·길게 누르기·취소 동작을 각각 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonMode -->

<!-- CARROT:SETTING:END CruiseButtonMode -->
