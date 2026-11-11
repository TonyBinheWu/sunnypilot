<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="LateralTorqueKiV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKi\*0.01(10)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKiV -->
<a id="LateralTorqueKiV"></a>

## \_LateralTorqueKi\*0.01(10)

`LateralTorqueKiV`

조향 누적 오차 보정 20 권장

<!-- CARROT:AUTO:BEGIN LateralTorqueKiV -->
<!-- CARROT:AUTO:SOURCE facts="e29f4b61611b9e1d0eaef728c202dcd318f78a55f7a2add65aa04a24b34353d5" semantic="1009f0b89dab98fe24e61983fa04ccf3c2daebed428a26b892370ecf0301a095" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `10`
- **범위:** `0` ~ `200`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKiV -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKiV -->
<!-- CARROT:REVIEW reviewed-for="1009f0b89dab98fe24e61983fa04ccf3c2daebed428a26b892370ecf0301a095" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

누적된 조향 오차를 보정하는 적분 계수입니다.

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
<!-- CARROT:MANUAL:END LateralTorqueKiV -->

<!-- CARROT:SETTING:END LateralTorqueKiV -->
