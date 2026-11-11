<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="LateralTorqueCustom" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueCustom(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN LateralTorqueCustom -->
<a id="LateralTorqueCustom"></a>

## \_LateralTorqueCustom(0)

`LateralTorqueCustom`

커스텀 토크 사용 (TorqueAccelFactor, FrictionFactor 사용을 위해서 켜기)

<!-- CARROT:AUTO:BEGIN LateralTorqueCustom -->
<!-- CARROT:AUTO:SOURCE facts="c32eb8e649ecb62ca52830d062c74762f41cc27e25e94d7d11ee079c94fedeee" semantic="931515b55fa1df2997b5da0e909ee948b8e957adb02298be36935346c8429d94" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `1`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueCustom -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueCustom -->
<!-- CARROT:REVIEW reviewed-for="931515b55fa1df2997b5da0e909ee948b8e957adb02298be36935346c8429d94" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 토크 제어에서 사용자 가속도·마찰·PID 계수를 읽어 적용합니다.
- **꺼짐:** 차량 인터페이스와 실시간 학습이 제공하는 기본 토크 계수를 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

토크 제어 차량에서 한 계수씩 작은 단계로 변경하고, 직선 복귀·완만한 커브·운전자 개입 시 토크를 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 커스텀 토크 계수는 토크 제어 차량에서만 의미가 있으며, 이 설정을 켜야 가속도 계수와 마찰 계수를 직접 사용합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LateralTorqueCustom -->

<!-- CARROT:SETTING:END LateralTorqueCustom -->
