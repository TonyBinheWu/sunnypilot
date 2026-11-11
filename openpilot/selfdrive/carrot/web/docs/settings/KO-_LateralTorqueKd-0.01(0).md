<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="LateralTorqueKd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKd\*0.01(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKd -->
<a id="LateralTorqueKd"></a>

## \_LateralTorqueKd\*0.01(0)

`LateralTorqueKd`

조향 미분 계수(급격한 변화에 저항) 0 권장

<!-- CARROT:AUTO:BEGIN LateralTorqueKd -->
<!-- CARROT:AUTO:SOURCE facts="4ef7c871d22a9038a233fe38623bb803f5edc8cba981d4cfd241bf689052a485" semantic="f4b07835f8d82647a8e9661e9116ca1f5478c8d37cdf844014eb000c7d90ea9a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `10000`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKd -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKd -->
<!-- CARROT:REVIEW reviewed-for="f4b07835f8d82647a8e9661e9116ca1f5478c8d37cdf844014eb000c7d90ea9a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

급격한 조향 오차 변화에 반응하는 미분 계수입니다.

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
<!-- CARROT:MANUAL:END LateralTorqueKd -->

<!-- CARROT:SETTING:END LateralTorqueKd -->
