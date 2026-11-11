<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="LatMpcMotionCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.MotionCost(7)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN LatMpcMotionCost -->
<a id="LatMpcMotionCost"></a>

## \*LATMPC.MotionCost(7)

`LatMpcMotionCost`

(레인모드) 헤딩가중치

<!-- CARROT:AUTO:BEGIN LatMpcMotionCost -->
<!-- CARROT:AUTO:SOURCE facts="62db1f934a755fac8be02719f0fecce4dc23ddbde748d8595a4b3900367c3ffa" semantic="1bdf8d77309360a95334d5df9779a59844b5330500ee823a8f43986ad8d5667f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `7`
- **범위:** `0` ~ `500`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcMotionCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcMotionCost -->
<!-- CARROT:REVIEW reviewed-for="1bdf8d77309360a95334d5df9779a59844b5330500ee823a8f43986ad8d5667f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(레인모드) 헤딩가중치.

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
<!-- CARROT:MANUAL:END LatMpcMotionCost -->

<!-- CARROT:SETTING:END LatMpcMotionCost -->
