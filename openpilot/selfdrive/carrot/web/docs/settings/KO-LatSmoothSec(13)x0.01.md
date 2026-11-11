<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_FEEL" param="LatSmoothSec" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LatSmoothSec(13)x0.01

**메뉴:** 주행 제어 \> 차량 조향 \> 조향감

---

<!-- CARROT:SETTING:BEGIN LatSmoothSec -->
<a id="LatSmoothSec"></a>

## LatSmoothSec(13)x0.01

`LatSmoothSec`

조향필터링값 높으면 부드러운조향

<!-- CARROT:AUTO:BEGIN LatSmoothSec -->
<!-- CARROT:AUTO:SOURCE facts="58984111f44d3e4c18716463c0f2814d6e72d2e4bdcbe27429fc0f2a64ffd657" semantic="42a46c7c6b551635f61326eed6731f5eccaa1f0669f7bb23fa20a4f8626c95c2" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `13`
- **범위:** `1` ~ `30`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 조향감
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatSmoothSec -->

<!-- CARROT:MANUAL:BEGIN LatSmoothSec -->
<!-- CARROT:REVIEW reviewed-for="42a46c7c6b551635f61326eed6731f5eccaa1f0669f7bb23fa20a4f8626c95c2" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

조향필터링값 / 높으면 부드러운조향.

- **값을 높이면:** 조향 변화가 더 부드럽고 느려집니다.
- **값을 낮추면:** 반응은 빨라지지만 변화가 거칠어질 수 있습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 직선과 완만한 커브에서 한 항목씩 작은 단계로 변경하고, 지연·진동·운전자 개입 후 복귀를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatSmoothSec -->

<!-- CARROT:SETTING:END LatSmoothSec -->
