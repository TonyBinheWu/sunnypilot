<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_CARROT" param="CarrotCruiseAtcDecel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 당근크루즈감속도ATCx0.01(-1)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈

---

<!-- CARROT:SETTING:BEGIN CarrotCruiseAtcDecel -->
<a id="CarrotCruiseAtcDecel"></a>

## 당근크루즈감속도ATCx0.01(-1)

`CarrotCruiseAtcDecel`

당근크루즈 ATC 감속도 지정 -1:변경안함

<!-- CARROT:AUTO:BEGIN CarrotCruiseAtcDecel -->
<!-- CARROT:AUTO:SOURCE facts="041eb64678c5636ffcdeb90c4e4eb42a674321eb664d6d4e61efca808cddf98b" semantic="a6733fcd86fb76d04b17b6518d26eb29a1989d9fad23e0faca06bbe22b4919a0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `-1`
- **범위:** `-1` ~ `200`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotCruiseAtcDecel -->

<!-- CARROT:MANUAL:BEGIN CarrotCruiseAtcDecel -->
<!-- CARROT:REVIEW reviewed-for="a6733fcd86fb76d04b17b6518d26eb29a1989d9fad23e0faca06bbe22b4919a0" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

당근크루즈 ATC 감속도 지정.

- **양수 값을 높이면:** ATC 중 당근 크루즈의 최대 감속 요청이 커집니다.
- **양수 값을 낮추면:** ATC 감속 요청 한도가 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원 차량과 해당 주행 모드에서 한 항목씩 변경하고, 목표 속도와 실제 가감속 요청을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 현재 코드에서는 지원되는 현대·기아 차량 제어기의 ATC 감속에만 적용됩니다. `-1`은 기존 감속 요청을 변경하지 않습니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CarrotCruiseAtcDecel -->

<!-- CARROT:SETTING:END CarrotCruiseAtcDecel -->
