<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_LONGTUNE" param="LongTuningKiV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Long KiV(0)x0.001

**메뉴:** 주행 제어 \> 크루즈·차간 \> 가감속 튜닝

---

<!-- CARROT:SETTING:BEGIN LongTuningKiV -->
<a id="LongTuningKiV"></a>

## Long KiV(0)x0.001

`LongTuningKiV`

롱컨 적분게인(누적오차 보정)입니다. 현대·기아·제네시스의 일반 종방향 제어는 Ki 0으로 고정되며 이 설정이 표시되거나 적용되지 않습니다. 토요타·렉서스는 전용 제어기의 보정을 중복하지 않도록 공통 Ki=0으로 고정되며 이 설정을 숨기고 저장값을 적용하지 않습니다. 레이 EV 콤마페달 제어가 차량 식별에서 확인되면 이 설정을 표시하고 저장값을 속도 PID에 적용합니다. 저장 후 약 1초 이내에 반영됩니다. 실제 Ki는 저장값 ×0.001입니다.

<!-- CARROT:AUTO:BEGIN LongTuningKiV -->
<!-- CARROT:AUTO:SOURCE facts="5f257422a42d5be0954982f8708a196bffcf856c29b8b516a1d5cb112fc0bf8b" semantic="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `2000`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 가감속 튜닝
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKiV -->

<!-- CARROT:MANUAL:BEGIN LongTuningKiV -->
<!-- CARROT:REVIEW reviewed-for="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" reviewed-at="2026-11-11T05:33:10.241824+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

누적된 속도 오차를 보정하는 종방향 적분 계수입니다.

- **값을 높이면:** 해당 종방향 제어 항의 영향이 커집니다.
- **값을 낮추면:** 해당 항의 영향이 줄어듭니다.

Volkswagen MEB(ID.4 포함)는 Kp와 Ki가 각각 단일 지점이므로 저장된 Kp/Ki/Kf 설정이 적용됩니다. 업데이트는 기존 저장값을 초기화하지 않습니다.
레이 EV에서 콤마페달이 인식되고 당근 종방향 제어가 활성화되면 Long Kp·Ki·Kf가 표시되고 저장값이 속도 PID에 적용됩니다. 시작할 때 저장값을 읽고 동작 중에는 약 1초마다 갱신합니다.

그 밖의 현대·기아·제네시스 구성은 공통 Kp/Ki/Kf가 1/0/1로 고정됩니다. 토요타·렉서스는 차량 전용 제어기가 가속도 추종을 보정하므로 공통 게인이 0/0/1로 고정됩니다.
Ki의 실제 계수는 저장값 × 0.001입니다. 저장값 50은 0.050, 100은 0.100으로 적용됩니다.
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
<!-- CARROT:MANUAL:END LongTuningKiV -->

<!-- CARROT:SETTING:END LongTuningKiV -->
