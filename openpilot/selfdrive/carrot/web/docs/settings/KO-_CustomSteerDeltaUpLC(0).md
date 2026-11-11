<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUpLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerDeltaUpLC(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUpLC -->
<a id="CustomSteerDeltaUpLC"></a>

## \_CustomSteerDeltaUpLC(0)

`CustomSteerDeltaUpLC`

(토크차량) 차선변경 시 일시적용 SteerDeltaUp

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:AUTO:SOURCE facts="78c72a8f981b6bfc8ec31111e7b7179c2b309db5b9bb95088eefe59d26699bdf" semantic="4c4f646026bac5f61b4baffbdf4b28f1bd790783dd022d744209c74a30c33e3e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `50`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUpLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:REVIEW reviewed-for="4c4f646026bac5f61b4baffbdf4b28f1bd790783dd022d744209c74a30c33e3e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(토크차량) / 차선변경 시 일시적용 SteerDeltaUp.

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
<!-- CARROT:MANUAL:END CustomSteerDeltaUpLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaUpLC -->
