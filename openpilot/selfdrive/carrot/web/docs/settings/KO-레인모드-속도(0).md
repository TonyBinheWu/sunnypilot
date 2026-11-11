<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="UseLaneLineSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 레인모드: 속도(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN UseLaneLineSpeed -->
<a id="UseLaneLineSpeed"></a>

## 레인모드: 속도(0)

`UseLaneLineSpeed`

설정 속도 이상일 때 레인모드를 사용합니다. 모델 속도 궤적의 시작값이 실제 차속의 70% 미만이거나 끝값이 시작값의 70% 미만이면 레인리스로 전환하며, 약 1초간 정상 조건을 확인한 뒤 복귀합니다.

<!-- CARROT:AUTO:BEGIN UseLaneLineSpeed -->
<!-- CARROT:AUTO:SOURCE facts="fe7250db3dcfeafe1f3a501238d683e757ff2e0c7d2d7b81e32ba2e1325362ba" semantic="9482c046d017df996fafb1a43bed6362e51c89952cf90e9d08991f354560e6f3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0km/h`
- **범위:** `0km/h` ~ `200km/h`
- **변경 단위:** `1`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseLaneLineSpeed -->

<!-- CARROT:MANUAL:BEGIN UseLaneLineSpeed -->
<!-- CARROT:REVIEW reviewed-for="c1d3fcc94fb373792b7f1ad242cc5c4b529b009b519117e53d940ac4ecd75043" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

설정 속도 이상일 때 레인모드로 전환합니다.

- **값을 높이면:** 적용되는 속도 또는 속도 기준이 높아집니다.
- **값을 낮추면:** 속도 또는 속도 기준이 낮아집니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 차선과 커브를 반복 주행하며 한 항목씩 조정하고, 경로 추종·조향 속도·부드러움을 함께 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0`이면 속도 기준 자동 전환을 사용하지 않습니다. 버튼으로 선택한 레인모드 상태는 별도로 유지될 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END UseLaneLineSpeed -->

<!-- CARROT:SETTING:END UseLaneLineSpeed -->
