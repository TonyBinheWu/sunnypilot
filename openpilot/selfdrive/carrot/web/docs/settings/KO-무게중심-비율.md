<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_FEEL" param="CenterToFrontRatio" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 무게중심 비율

**메뉴:** 주행 제어 \> 차량 조향 \> 조향감

---

<!-- CARROT:SETTING:BEGIN CenterToFrontRatio -->
<a id="CenterToFrontRatio"></a>

## 무게중심 비율

`CenterToFrontRatio`

0=차종별 기본값. 그 외 31~69%=휠베이스×비율. 저장하면 재시작 없이 부드럽게 반영됩니다. 기본: 현대·기아·제네시스 40%, 토요타·렉서스 44%, 마쓰다 41%, 폭스바겐 45%, 혼다는 차종별 상이. 진입이 늦으면 ↑, 초입에 파고들면 ↓를 소폭 비교하세요. 효과는 차선 모드·차량에 따라 다릅니다. SAD·SR은 유지하고 하나씩 조절하세요. 악화되면 이전 값이나 0으로 복원하세요.

<!-- CARROT:AUTO:BEGIN CenterToFrontRatio -->
<!-- CARROT:AUTO:SOURCE facts="706bd8909b807d26e7cd0b9894329b9bd9cc75dffcef679e78ce5616692745ba" semantic="ffcefcd7552894afdf0dbf200567b02117bac3fdd8a60a8f29a28907d3976f52" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0%`
- **범위:** `0%` ~ `69%`
- **변경 단위:** `1`
- **표시 단위:** `%`
- **메뉴:** 주행 제어 \> 차량 조향 \> 조향감
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CenterToFrontRatio -->

<!-- CARROT:MANUAL:BEGIN CenterToFrontRatio -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CenterToFrontRatio -->

<!-- CARROT:SETTING:END CenterToFrontRatio -->
