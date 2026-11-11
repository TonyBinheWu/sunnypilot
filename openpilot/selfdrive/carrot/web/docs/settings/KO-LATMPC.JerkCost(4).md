<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="LatMpcJerkCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.JerkCost(4)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN LatMpcJerkCost -->
<a id="LatMpcJerkCost"></a>

## \*LATMPC.JerkCost(4)

`LatMpcJerkCost`

(레인모드) 낮추면 빠른조향허용 부드러움 감소

<!-- CARROT:AUTO:BEGIN LatMpcJerkCost -->
<!-- CARROT:AUTO:SOURCE facts="6428d93722e8df0356d319536555316a85f3a7c2d48a3becf9101af3a73fe062" semantic="b03aeed762639a7ad9e574bc0a93999bce2ccf72dd07f737014001472e26b1fb" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `1`
- **범위:** `0` ~ `200`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcJerkCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcJerkCost -->
<!-- CARROT:REVIEW reviewed-for="b03aeed762639a7ad9e574bc0a93999bce2ccf72dd07f737014001472e26b1fb" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(레인모드) 낮추면 빠른조향허용 / 부드러움 감소.

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
<!-- CARROT:MANUAL:END LatMpcJerkCost -->

<!-- CARROT:SETTING:END LatMpcJerkCost -->
