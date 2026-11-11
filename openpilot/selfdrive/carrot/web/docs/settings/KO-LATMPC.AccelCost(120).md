<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="LatMpcAccelCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.AccelCost(120)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN LatMpcAccelCost -->
<a id="LatMpcAccelCost"></a>

## \*LATMPC.AccelCost(120)

`LatMpcAccelCost`

(레인모드) 횡가속도제한 낮으면 민첩성증가 안정성감소

<!-- CARROT:AUTO:BEGIN LatMpcAccelCost -->
<!-- CARROT:AUTO:SOURCE facts="611a30cd94908b5e6009e95f7ae0c316395722bdc66263d2f9836be01780dbcf" semantic="8538f6cbd23edf0ba7f4d95ad4afb9b20e5a66792ca42c8559874d43490b0ca6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `100`
- **범위:** `0` ~ `500`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcAccelCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcAccelCost -->
<!-- CARROT:REVIEW reviewed-for="8538f6cbd23edf0ba7f4d95ad4afb9b20e5a66792ca42c8559874d43490b0ca6" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(레인모드) 횡가속도제한 / 낮으면 민첩성증가 안정성감소.

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
<!-- CARROT:MANUAL:END LatMpcAccelCost -->

<!-- CARROT:SETTING:END LatMpcAccelCost -->
