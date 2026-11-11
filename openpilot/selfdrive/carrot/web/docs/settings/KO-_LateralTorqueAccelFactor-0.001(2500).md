<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="LateralTorqueAccelFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueAccelFactor\*0.001(2500)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN LateralTorqueAccelFactor -->
<a id="LateralTorqueAccelFactor"></a>

## \_LateralTorqueAccelFactor\*0.001(2500)

`LateralTorqueAccelFactor`

낮을수록 토크가 강해지다가 어느순간 약해짐 가장 강한 지점의 값 사용

<!-- CARROT:AUTO:BEGIN LateralTorqueAccelFactor -->
<!-- CARROT:AUTO:SOURCE facts="a9a20638424e5cd06423d209aef967811d280bbebe15391d5b5abf0be5a4a807" semantic="746c0daa75a2f8c2391948cd47d2956c33436ee89b75ae1080fe4a6a40d6d552" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `2500`
- **범위:** `1000` ~ `6000`
- **변경 단위:** `100`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueAccelFactor -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueAccelFactor -->
<!-- CARROT:REVIEW reviewed-for="746c0daa75a2f8c2391948cd47d2956c33436ee89b75ae1080fe4a6a40d6d552" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

요청 횡가속도를 조향 토크로 변환하는 계수입니다.

값을 낮출수록 토크가 강해지다가 특정 지점을 지나면 다시 약해지는 비선형 계수입니다. 가장 강한 지점을 실제 차량에서 작은 단계로 찾아야 합니다.
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
<!-- CARROT:MANUAL:END LateralTorqueAccelFactor -->

<!-- CARROT:SETTING:END LateralTorqueAccelFactor -->
