<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_CARROT" param="CarrotCruiseDecel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 당근크루즈감속도x0.01(-1)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈

---

<!-- CARROT:SETTING:BEGIN CarrotCruiseDecel -->
<a id="CarrotCruiseDecel"></a>

## 당근크루즈감속도x0.01(-1)

`CarrotCruiseDecel`

당근크루즈 감속도 지정 -1:크루즈OFF

<!-- CARROT:AUTO:BEGIN CarrotCruiseDecel -->
<!-- CARROT:AUTO:SOURCE facts="0e98ade5308b8dfdd47c215c58fb7099f902218cd77ccbd235138122f2f0fd69" semantic="ba7e233d65895feac8118c77053f75720240197ed3ffa0ecf87ea2f953e899d2" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `-1`
- **범위:** `-1` ~ `200`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotCruiseDecel -->

<!-- CARROT:MANUAL:BEGIN CarrotCruiseDecel -->
<!-- CARROT:REVIEW reviewed-for="ba7e233d65895feac8118c77053f75720240197ed3ffa0ecf87ea2f953e899d2" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

당근크루즈 감속도 지정.

- **양수 값을 높이면:** 당근 크루즈의 최대 감속 요청이 커집니다.
- **양수 값을 낮추면:** 허용하는 감속 요청이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원 차량과 해당 주행 모드에서 한 항목씩 변경하고, 목표 속도와 실제 가감속 요청을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 현재 코드에서는 지원되는 현대·기아 차량 제어기에만 적용됩니다. `-1`은 당근 크루즈 감속 요청 대신 크루즈 해제 동작을 사용합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CarrotCruiseDecel -->

<!-- CARROT:SETTING:END CarrotCruiseDecel -->
