<!-- CARROT:GENERATED schema="1" locale="ko" group="DAILY_DRIVING" param="DynamicExperimentalControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 동적 실험 모드 (DEC)

**메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행

---

<!-- CARROT:SETTING:BEGIN DynamicExperimentalControl -->
<a id="DynamicExperimentalControl"></a>

## 동적 실험 모드 (DEC)

`DynamicExperimentalControl`

openpilot 종방향 제어에서 다음 주행부터 적용합니다. 켜면 도로 상황에 따라 ACC와 모델 협조 모드를 전환합니다. 끄면 모델, 차간거리, 설정 속도를 계속 비교합니다.

<!-- CARROT:AUTO:BEGIN DynamicExperimentalControl -->
<!-- CARROT:AUTO:SOURCE facts="a49769cad7abd299dc353987cab727ac5f30fcbcefa11d73cf1434822a68bb96" semantic="a7a764b20cbe66993b48c48e82db9071065d70108e424f5ae323dde2cf4d87d8" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DynamicExperimentalControl -->

<!-- CARROT:MANUAL:BEGIN DynamicExperimentalControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END DynamicExperimentalControl -->

<!-- CARROT:SETTING:END DynamicExperimentalControl -->
