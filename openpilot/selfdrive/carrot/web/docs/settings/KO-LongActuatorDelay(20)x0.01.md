<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_LONGTUNE" param="LongActuatorDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LongActuatorDelay(20)x0.01

**메뉴:** 주행 제어 \> 크루즈·차간 \> 가감속 튜닝

---

<!-- CARROT:SETTING:BEGIN LongActuatorDelay -->
<a id="LongActuatorDelay"></a>

## LongActuatorDelay(20)x0.01

`LongActuatorDelay`

롱컨 지연값(높을수록 미리 가감속) HKG: 20으로 설정 권장

<!-- CARROT:AUTO:BEGIN LongActuatorDelay -->
<!-- CARROT:AUTO:SOURCE facts="86c8598d8be0e6e22624bff6bc552c7649bce34398fcd896eaccf4ca4fe5c6cc" semantic="83f945e2bbe7928bc6258df845c0f2c9ea2701fa8ecf7a6225873c62d3a181cc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `20`
- **범위:** `0` ~ `200`
- **변경 단위:** `5`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 가감속 튜닝
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongActuatorDelay -->

<!-- CARROT:MANUAL:BEGIN LongActuatorDelay -->
<!-- CARROT:REVIEW reviewed-for="83f945e2bbe7928bc6258df845c0f2c9ea2701fa8ecf7a6225873c62d3a181cc" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

가속·제동 요청부터 차량 반응까지의 지연을 보정합니다.

- **값을 높이면:** 가속·감속 지연을 크게 보고 목표 변화를 더 일찍 요청합니다.
- **값을 낮추면:** 종방향 선행 보정이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 목표 속도 변화에서 한 계수씩 작은 단계로 조정하고, 오버슈트·진동·반응 지연을 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LongActuatorDelay -->

<!-- CARROT:SETTING:END LongActuatorDelay -->
