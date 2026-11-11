<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANEMODE" param="UseLaneLineCurveSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 레인모드: 커브속도(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 레인모드

---

<!-- CARROT:SETTING:BEGIN UseLaneLineCurveSpeed -->
<a id="UseLaneLineCurveSpeed"></a>

## 레인모드: 커브속도(0)

`UseLaneLineCurveSpeed`

레인모드를 설정속도 이하에서는 사용하지 않습니다.

<!-- CARROT:AUTO:BEGIN UseLaneLineCurveSpeed -->
<!-- CARROT:AUTO:SOURCE facts="4a2ba2db5065867fbf153c7f425d2a186a4b750645f2e23a38a7b38fdb1a5972" semantic="ba0eea8757a1b91d43653961d6c80ce6c8384ba9524d5ee91a71df24e30beb5e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0km/h`
- **범위:** `0km/h` ~ `200km/h`
- **변경 단위:** `10`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 차량 조향 \> 레인모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseLaneLineCurveSpeed -->

<!-- CARROT:MANUAL:BEGIN UseLaneLineCurveSpeed -->
<!-- CARROT:REVIEW reviewed-for="ba0eea8757a1b91d43653961d6c80ce6c8384ba9524d5ee91a71df24e30beb5e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

레인모드를 설정속도 이하에서는 사용하지 않습니다.

- **값을 높이면:** 적용되는 속도 또는 속도 기준이 높아집니다.
- **값을 낮추면:** 속도 또는 속도 기준이 낮아집니다.
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
<!-- CARROT:MANUAL:END UseLaneLineCurveSpeed -->

<!-- CARROT:SETTING:END UseLaneLineCurveSpeed -->
