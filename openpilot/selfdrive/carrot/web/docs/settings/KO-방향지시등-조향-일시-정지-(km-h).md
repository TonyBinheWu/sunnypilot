<!-- CARROT:GENERATED schema="1" locale="ko" group="DAILY_DRIVING" param="SunnyBlinkerPauseKph" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 방향지시등 조향 일시 정지 (km/h)

**메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행

---

<!-- CARROT:SETTING:BEGIN SunnyBlinkerPauseKph -->
<a id="SunnyBlinkerPauseKph"></a>

## 방향지시등 조향 일시 정지 (km/h)

`SunnyBlinkerPauseKph`

모델 + 차간거리 제어에서 다음 주행부터 적용. 0은 꺼짐입니다. 설정 속도 미만에서 한쪽 방향지시등을 켜면 조향을 일시 정지합니다.

<!-- CARROT:AUTO:BEGIN SunnyBlinkerPauseKph -->
<!-- CARROT:AUTO:SOURCE facts="5e4932af86ee43d77d664bddbad392a8243d2edb2b687d232e80c845654eccce" semantic="49fff7c9b8de6f29293c0c3f9603a7ed153258de03b3b3f959c81becee0952ed" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `30`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 일상 주행
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SunnyBlinkerPauseKph -->

<!-- CARROT:MANUAL:BEGIN SunnyBlinkerPauseKph -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SunnyBlinkerPauseKph -->

<!-- CARROT:SETTING:END SunnyBlinkerPauseKph -->
