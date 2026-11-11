<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="LatMpcInputOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.InputOffset(4)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN LatMpcInputOffset -->
<a id="LatMpcInputOffset"></a>

## \*LATMPC.InputOffset(4)

`LatMpcInputOffset`

(레인모드) Mpc입력보상 값이 크면 일찍커브에 진입함

<!-- CARROT:AUTO:BEGIN LatMpcInputOffset -->
<!-- CARROT:AUTO:SOURCE facts="cf0fd6516a2adc0433371ce6bd95da3cad1a055035c6b6e8857cb7490d8a52b2" semantic="efc63caea6708ae570390d3c639d780d27edaa7d333175c03cd31e82d16b81cf" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `4`
- **범위:** `0` ~ `20`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcInputOffset -->

<!-- CARROT:MANUAL:BEGIN LatMpcInputOffset -->
<!-- CARROT:REVIEW reviewed-for="efc63caea6708ae570390d3c639d780d27edaa7d333175c03cd31e82d16b81cf" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(레인모드) Mpc입력보상 / 값이 크면 일찍커브에 진입함.

- **값을 높이면:** MPC 입력을 더 앞당겨 커브에 일찍 반응합니다.
- **값을 낮추면:** 커브 반응 시점이 늦어집니다.
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
<!-- CARROT:MANUAL:END LatMpcInputOffset -->

<!-- CARROT:SETTING:END LatMpcInputOffset -->
