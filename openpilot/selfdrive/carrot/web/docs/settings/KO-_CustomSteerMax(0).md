<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_LIMIT" param="CustomSteerMax" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerMax(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한

---

<!-- CARROT:SETTING:BEGIN CustomSteerMax -->
<a id="CustomSteerMax"></a>

## \_CustomSteerMax(0)

`CustomSteerMax`

최대조향토크 270/384/409 중 오류가 안나는 가장 큰 값 사용

<!-- CARROT:AUTO:BEGIN CustomSteerMax -->
<!-- CARROT:AUTO:SOURCE facts="f38a1f13f1c7576540a483e156cbe7059b800e19f6051da785c1ad975b370cd8" semantic="669ef6b96724cee684584bacd4c6c1cce990b4de53df8969d58d5f175dc0e1ed" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `30000`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerMax -->

<!-- CARROT:MANUAL:BEGIN CustomSteerMax -->
<!-- CARROT:REVIEW reviewed-for="669ef6b96724cee684584bacd4c6c1cce990b4de53df8969d58d5f175dc0e1ed" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

지원되는 현대·기아 토크 제어기의 최대 조향 토크 한도를 조정합니다.

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
<!-- CARROT:MANUAL:END CustomSteerMax -->

<!-- CARROT:SETTING:END CustomSteerMax -->
