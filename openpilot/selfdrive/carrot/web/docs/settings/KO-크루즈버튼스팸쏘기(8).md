<!-- CARROT:GENERATED schema="1" locale="ko" group="BUTTON_TEST" param="CruiseButtonTest1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 크루즈버튼스팸쏘기(8)

**메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 테스트

---

<!-- CARROT:SETTING:BEGIN CruiseButtonTest1 -->
<a id="CruiseButtonTest1"></a>

## 크루즈버튼스팸쏘기(8)

`CruiseButtonTest1`

(비롱컨 전용) 속도버튼신호 발송제한시간

<!-- CARROT:AUTO:BEGIN CruiseButtonTest1 -->
<!-- CARROT:AUTO:SOURCE facts="22a92d598fcb640873059d0f3530853d653df9f1cea0d75488295987214211ec" semantic="b76fc3c2fedf34451067daab249e5a3933c4cbbe94d61cbb0fd5198798b31a2f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `1` ~ `20`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 버튼·프리셋 \> 버튼 테스트
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonTest1 -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonTest1 -->
<!-- CARROT:REVIEW reviewed-for="b76fc3c2fedf34451067daab249e5a3933c4cbbe94d61cbb0fd5198798b31a2f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(비롱컨 전용) 속도버튼신호 발송제한시간.

- **값을 높이면:** 한 번에 버튼 신호를 보내는 구간이 길어집니다.
- **값을 낮추면:** 전송 구간이 짧아집니다.
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
<!-- CARROT:MANUAL:END CruiseButtonTest1 -->

<!-- CARROT:SETTING:END CruiseButtonTest1 -->
