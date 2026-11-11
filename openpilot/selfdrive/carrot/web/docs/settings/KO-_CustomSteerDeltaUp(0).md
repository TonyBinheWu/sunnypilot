<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUp" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerDeltaUp(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUp -->
<a id="CustomSteerDeltaUp"></a>

## \_CustomSteerDeltaUp(0)

`CustomSteerDeltaUp`

(토크차량) 높을수록 핸들 감는속도 빨라짐

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:AUTO:SOURCE facts="1a46cae0a2cbe97f8c05ce7eb3b16312f199d47359d360664aafe69e46b3c3af" semantic="22505d7f9d2fdc5441ecca4890ef75dd0dd73869c71f0347effa2d7f6d892664" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `50`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUp -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:REVIEW reviewed-for="22505d7f9d2fdc5441ecca4890ef75dd0dd73869c71f0347effa2d7f6d892664" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(토크차량) / 높을수록 핸들 감는속도 빨라짐.

- **값을 높이면:** 해당 조향 토크 한도 또는 변화율이 커집니다.
- **값을 낮추면:** 한도 또는 변화율이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원되는 토크 제어 차량에서 한 항목씩 조정하고, 정상 주행과 차선 변경에서 조향 증가·감소 속도를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSteerDeltaUp -->

<!-- CARROT:SETTING:END CustomSteerDeltaUp -->
