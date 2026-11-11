<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="LatMpcPathCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.PathCost(200)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN LatMpcPathCost -->
<a id="LatMpcPathCost"></a>

## \*LATMPC.PathCost(200)

`LatMpcPathCost`

(레인모드) 경로추종가중치 높으면 경로우선시함.

<!-- CARROT:AUTO:BEGIN LatMpcPathCost -->
<!-- CARROT:AUTO:SOURCE facts="e72cb9e9b534f1bca4960e56b00d4df2cd113c0ecaa2e5267551ba52ac61dfef" semantic="b83cc299182908b4d8c01ed9a897df4983bc1c8e59c535005d5f9ddde372c233" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `200`
- **범위:** `0` ~ `500`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcPathCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcPathCost -->
<!-- CARROT:REVIEW reviewed-for="b83cc299182908b4d8c01ed9a897df4983bc1c8e59c535005d5f9ddde372c233" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(레인모드) 경로추종가중치 / 높으면 경로우선시함.

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
<!-- CARROT:MANUAL:END LatMpcPathCost -->

<!-- CARROT:SETTING:END LatMpcPathCost -->
