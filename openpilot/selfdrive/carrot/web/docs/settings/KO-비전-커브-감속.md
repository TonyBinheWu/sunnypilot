<!-- CARROT:GENERATED schema="1" locale="ko" group="DAILY_DRIVING" param="SunnyVisionCurve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 비전 커브 감속

**메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행

---

<!-- CARROT:SETTING:BEGIN SunnyVisionCurve -->
<a id="SunnyVisionCurve"></a>

## 비전 커브 감속

`SunnyVisionCurve`

모델 + 차간거리 제어에서 다음 주행부터 적용. 모델의 예상 횡가속도에 따라 추가 감속합니다. 꺼도 모델 자체 감속은 유지됩니다.

<!-- CARROT:AUTO:BEGIN SunnyVisionCurve -->
<!-- CARROT:AUTO:SOURCE facts="e61e186cf1dbec6fabc67871fd96c890dd1a8f4a64db6f2f9175258ff48b83fd" semantic="c6b646e22c50917763853a297c5134b896a7186b3376ab2c71af1a1d1cc20ea7" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SunnyVisionCurve -->

<!-- CARROT:MANUAL:BEGIN SunnyVisionCurve -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SunnyVisionCurve -->

<!-- CARROT:SETTING:END SunnyVisionCurve -->
