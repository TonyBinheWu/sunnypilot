<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="LateralTorqueFriction" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueFriction\*0.001(100)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN LateralTorqueFriction -->
<a id="LateralTorqueFriction"></a>

## \_LateralTorqueFriction\*0.001(100)

`LateralTorqueFriction`

높을수록 미세조향이 많아짐 0~50 권장

<!-- CARROT:AUTO:BEGIN LateralTorqueFriction -->
<!-- CARROT:AUTO:SOURCE facts="458418e94b762cf82e055c9cfb67b8195c61bb657f2a75b7233c3148896dfc67" semantic="bcb493a10728312a73f302531a0693387e121c32f1573d25390eaa2d30c5454a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `100`
- **범위:** `0` ~ `1000`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueFriction -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueFriction -->
<!-- CARROT:REVIEW reviewed-for="bcb493a10728312a73f302531a0693387e121c32f1573d25390eaa2d30c5454a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

조향계 마찰을 보상하는 토크 계수입니다.

- **값을 높이면:** 마찰 보상이 커져 미세 조향 토크가 증가합니다.
- **값을 낮추면:** 마찰 보상과 미세 조향 토크가 줄어듭니다.
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
<!-- CARROT:MANUAL:END LateralTorqueFriction -->

<!-- CARROT:SETTING:END LateralTorqueFriction -->
