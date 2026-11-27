<!-- CARROT:GENERATED schema="1" locale="ko" group="DAILY_DRIVING" param="SunnyCruisePlanner" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 순항 속도 계획

**메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행

---

<!-- CARROT:SETTING:BEGIN SunnyCruisePlanner -->
<a id="SunnyCruisePlanner"></a>

## 순항 속도 계획

`SunnyCruisePlanner`

다음 주행부터 적용. 0은 기존 계획기, 1은 sunnypilot 순항과 레이더·카메라 선행차, 2는 같은 순항과 카메라 선행차만 사용합니다. DEC를 켜면 실험 모드에서 주행 상황에 따라 전환합니다.

<!-- CARROT:AUTO:BEGIN SunnyCruisePlanner -->
<!-- CARROT:AUTO:SOURCE facts="1419c37468a0f8ace8e80c3f81b745306cae37bd3a6422ff5c1984c73418141a" semantic="c38bc552088c099ef8b690307d86f5d076d3fce258662e3c4042e827d3a7bd3d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 기존 계획기 (`0`)
- **범위:** 기존 계획기 (`0`) ~ sunnypilot · 카메라 선행차 (`2`)
- **변경 단위:** `1`
- **선택지:** `0` 기존 계획기, `1` sunnypilot · 차량 센서, `2` sunnypilot · 카메라 선행차
- **메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SunnyCruisePlanner -->

<!-- CARROT:MANUAL:BEGIN SunnyCruisePlanner -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SunnyCruisePlanner -->

<!-- CARROT:SETTING:END SunnyCruisePlanner -->
