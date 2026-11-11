<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="LatMpcSteeringRateCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.SteerRateCost(7)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN LatMpcSteeringRateCost -->
<a id="LatMpcSteeringRateCost"></a>

## \*LATMPC.SteerRateCost(7)

`LatMpcSteeringRateCost`

(레인모드) 조향변화율제한 낮추면 조향이 적극적

<!-- CARROT:AUTO:BEGIN LatMpcSteeringRateCost -->
<!-- CARROT:AUTO:SOURCE facts="7e8b3a8023363166b16deaa87a75d2abca9f72cd6decc0283e3968a96acedf0a" semantic="abb62754276e8852ac2b76df32326edddc868ac4e65e04789efd359aa48f1f74" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `7`
- **범위:** `0` ~ `1000`
- **변경 단위:** `100`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcSteeringRateCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcSteeringRateCost -->
<!-- CARROT:REVIEW reviewed-for="abb62754276e8852ac2b76df32326edddc868ac4e65e04789efd359aa48f1f74" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(레인모드) 조향변화율제한 / 낮추면 조향이 적극적.

- **값을 높이면:** 해당 항목의 MPC 비용과 억제 비중이 커집니다.
- **값을 낮추면:** 해당 움직임을 더 적극적으로 허용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 차선과 커브를 반복 주행하며 한 항목씩 조정하고, 경로 추종·조향 속도·부드러움을 함께 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatMpcSteeringRateCost -->

<!-- CARROT:SETTING:END LatMpcSteeringRateCost -->
