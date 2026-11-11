<!-- CARROT:GENERATED schema="1" locale="ko" group="BUTTON_TEST" param="CruiseButtonTest3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 크루즈버튼스팸연속쏘기(1)

**메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 테스트

---

<!-- CARROT:SETTING:BEGIN CruiseButtonTest3 -->
<a id="CruiseButtonTest3"></a>

## 크루즈버튼스팸연속쏘기(1)

`CruiseButtonTest3`

(비롱컨 전용) 속도버튼신호 연속회수

<!-- CARROT:AUTO:BEGIN CruiseButtonTest3 -->
<!-- CARROT:AUTO:SOURCE facts="0e3c2044351e6b273584ed3701e719eabb470951744cda03f1be5ff33095be9e" semantic="af261696361d69a11ca78c75dec91ea37bd659d2db7fd9b1cb1ba1a8c17aa391" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `1` ~ `20`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 테스트
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonTest3 -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonTest3 -->
<!-- CARROT:REVIEW reviewed-for="af261696361d69a11ca78c75dec91ea37bd659d2db7fd9b1cb1ba1a8c17aa391" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(비롱컨 전용) 속도버튼신호 연속회수.

- **값을 높이면:** 연속으로 보내는 버튼 신호 횟수가 늘어납니다.
- **값을 낮추면:** 연속 전송 횟수가 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

순정 SCC 버튼 신호를 사용하는 비롱컨 차량에서만 조정하고, 한 항목씩 바꾸며 버튼 누락이나 과다 입력이 없는지 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 비롱컨 차량의 순정 SCC 버튼 메시지에 직접 영향을 줍니다. 검증된 차량에서만 기본값을 기록한 뒤 조정합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonTest3 -->

<!-- CARROT:SETTING:END CruiseButtonTest3 -->
