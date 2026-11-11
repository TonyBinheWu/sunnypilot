<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_FEEL" param="CustomSR" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CustomSteerRatiox0.1(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 조향감

---

<!-- CARROT:SETTING:BEGIN CustomSR -->
<a id="CustomSR"></a>

## CustomSteerRatiox0.1(0)

`CustomSR`

조향비(차량제원 참고) 0: LiveSteerRatio 사용

<!-- CARROT:AUTO:BEGIN CustomSR -->
<!-- CARROT:AUTO:SOURCE facts="585e690b39fa3e5e36ceac374096fcf034d9df941375dda0319f8021e45949fd" semantic="ac448bdc0d0511e23b7beef678bc36d35b02b4610877afe79699ea4a590e9210" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `300`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 조향감
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSR -->

<!-- CARROT:MANUAL:BEGIN CustomSR -->
<!-- CARROT:REVIEW reviewed-for="ac448bdc0d0511e23b7beef678bc36d35b02b4610877afe79699ea4a590e9210" reviewed-at="2026-09-30T12:27:06.518422+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

조향비(차량제원 참고).

- **값을 높이면:** 고정 조향비가 커져 같은 곡률에 필요한 조향각 계산이 달라집니다.
- **값을 낮추면:** 고정 조향비가 작아집니다.

VW MEB(ID.4 포함)에도 적용되며, 변경한 값은 제어 중 다시 읽습니다. 설정값을 0.1배 한 조향비가 1.0보다 크면 수동값을 사용하고, 그 외에는 학습값과 `SteerRatioRate`를 사용합니다. 수동값 선택은 SR 학습 자체를 중지하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 직선과 완만한 커브에서 한 항목씩 작은 단계로 변경하고, 지연·진동·운전자 개입 후 복귀를 확인합니다.

이전에 ID.4에서 무시되던 저장값도 업데이트 후 적용됩니다. 학습 조향비를 그대로 사용하려면 `CustomSR=0`, `SteerRatioRate=100%`로 설정합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> `0`이면 학습된 조향비를 사용합니다. 직접 값을 지정하면 `SteerRatioRate` 배율보다 이 값이 우선합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSR -->

<!-- CARROT:SETTING:END CustomSR -->
