<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="LateralTorqueKpV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKp\*0.01(100)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKpV -->
<a id="LateralTorqueKpV"></a>

## \_LateralTorqueKp\*0.01(100)

`LateralTorqueKpV`

조향 비례 계수(오차가 클수록 강하게 반응) 140 권장

<!-- CARROT:AUTO:BEGIN LateralTorqueKpV -->
<!-- CARROT:AUTO:SOURCE facts="519b3e6232bcb9da6b83726cac18f63c4b50de7b5befb3a30b28bd0bffe491e5" semantic="03a3a5b716a1a1c2a0bb05b45da9e8adcadcf2e1c1a3232e2fbc606fc1ab928a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `100`
- **범위:** `0` ~ `200`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKpV -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKpV -->
<!-- CARROT:REVIEW reviewed-for="03a3a5b716a1a1c2a0bb05b45da9e8adcadcf2e1c1a3232e2fbc606fc1ab928a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

조향 오차에 즉시 반응하는 비례 계수입니다.

- **값을 높이면:** 해당 토크 제어 항의 영향이 커집니다.
- **값을 낮추면:** 해당 항의 영향이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

토크 제어 차량에서 한 계수씩 작은 단계로 변경하고, 직선 복귀·완만한 커브·운전자 개입 시 토크를 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LateralTorqueKpV -->

<!-- CARROT:SETTING:END LateralTorqueKpV -->
