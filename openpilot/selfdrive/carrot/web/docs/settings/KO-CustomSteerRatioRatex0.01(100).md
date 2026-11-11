<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_FEEL" param="SteerRatioRate" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CustomSteerRatioRatex0.01(100)

**메뉴:** 주행 제어 \> 차량 조향 \> 조향감

---

<!-- CARROT:SETTING:BEGIN SteerRatioRate -->
<a id="SteerRatioRate"></a>

## CustomSteerRatioRatex0.01(100)

`SteerRatioRate`

LiveSteerRatio 반영비율 (CustomSR 0으로 설정해야 함)

<!-- CARROT:AUTO:BEGIN SteerRatioRate -->
<!-- CARROT:AUTO:SOURCE facts="40581abc61c961fd27c3f2b1225608a7e62f398b396d79ce060564d8f433a005" semantic="3dcdc5b26050ba384382fe8733f365d2de9ff1bc73e56b23703f73b6dce4381b" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `100%`
- **범위:** `30%` ~ `200%`
- **변경 단위:** `1`
- **표시 단위:** `%`
- **메뉴:** 주행 제어 \> 차량 조향 \> 조향감
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SteerRatioRate -->

<!-- CARROT:MANUAL:BEGIN SteerRatioRate -->
<!-- CARROT:REVIEW reviewed-for="3dcdc5b26050ba384382fe8733f365d2de9ff1bc73e56b23703f73b6dce4381b" reviewed-at="2026-09-30T12:27:06.518422+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

LiveSteerRatio 반영비율 / (CustomSR 0으로 설정해야 함).

- **값을 높이면:** 학습 조향비에 적용하는 배율이 커집니다.
- **값을 낮추면:** 학습 조향비 배율이 작아집니다.

VW MEB(ID.4 포함)에도 적용되며, 수동 조향비가 선택되면 이 비율은 사용하지 않습니다. 허용 범위를 벗어난 저장 비율은 학습값을 그대로 사용하는 비율로 대체합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 직선과 완만한 커브에서 한 항목씩 작은 단계로 변경하고, 지연·진동·운전자 개입 후 복귀를 확인합니다.

이전에 ID.4에서 무시되던 저장값도 업데이트 후 적용됩니다. 학습 조향비를 그대로 사용하려면 `CustomSR=0`, `SteerRatioRate=100%`로 설정합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> `CustomSR`이 `0`일 때만 학습된 조향비에 이 배율이 적용됩니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SteerRatioRate -->

<!-- CARROT:SETTING:END SteerRatioRate -->
