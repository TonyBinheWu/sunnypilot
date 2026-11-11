<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="LateralTorqueKf" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKf\*0.01(100)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKf -->
<a id="LateralTorqueKf"></a>

## \_LateralTorqueKf\*0.01(100)

`LateralTorqueKf`

조향 예측 기반 보정 85 권장

<!-- CARROT:AUTO:BEGIN LateralTorqueKf -->
<!-- CARROT:AUTO:SOURCE facts="bbfb1a446dbd71779234c427630221414f8f04d1678b49531a0984c83113d845" semantic="ea6d27099c3e8610130f74384cd9fe8bee6c2a22a6291c942b50541fc25fcd81" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `100`
- **범위:** `0` ~ `200`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKf -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKf -->
<!-- CARROT:REVIEW reviewed-for="ea6d27099c3e8610130f74384cd9fe8bee6c2a22a6291c942b50541fc25fcd81" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

예측 조향 토크에 적용하는 피드포워드 계수입니다.

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
<!-- CARROT:MANUAL:END LateralTorqueKf -->

<!-- CARROT:SETTING:END LateralTorqueKf -->
