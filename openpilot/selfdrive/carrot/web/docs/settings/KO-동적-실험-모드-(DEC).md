<!-- CARROT:GENERATED schema="1" locale="ko" group="DAILY_DRIVING" param="DynamicExperimentalControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 동적 실험 모드 (DEC)

**메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행

---

<!-- CARROT:SETTING:BEGIN DynamicExperimentalControl -->
<a id="DynamicExperimentalControl"></a>

## 동적 실험 모드 (DEC)

`DynamicExperimentalControl`

openpilot 종방향 제어에서 다음 주행부터 적용합니다. 기본값은 꺼짐입니다. 전방에 차가 없음을 확인하면 설정 속도 한도 내에서 모델이 가속도를 결정합니다. 켜면 도로 상황에 따라 ACC와 모델 협조 모드를 전환합니다.

<!-- CARROT:AUTO:BEGIN DynamicExperimentalControl -->
<!-- CARROT:AUTO:SOURCE facts="782337a54519004d16ed04b564f1e68f7fb77a0b01ac45fcfec00fe03e3ebf51" semantic="812cd842d2e82c6f1efab61b169f7a27f6ca8a20c4399a0143bf5fb7f7405fcd" review="needs_review" -->
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
