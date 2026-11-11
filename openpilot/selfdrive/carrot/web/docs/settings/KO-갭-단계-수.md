<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="CruiseGapLevels" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 갭 단계 수

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN CruiseGapLevels -->
<a id="CruiseGapLevels"></a>

## 갭 단계 수

`CruiseGapLevels`

갭 버튼으로 순환할 단계 수입니다. 2단계부터 차량 지원 최대 단계까지 선택하며 기본값은 차량 최대 단계입니다. 2는 TF1↔TF2, 3은 TF1~TF3을 사용합니다. 다음 갭 버튼 조작부터 적용하며 사용하지 않는 TF와 추종응답성 값도 보관합니다. openpilot이 가감속을 제어할 때 적용하며 순정 ACC의 단계 수는 바꾸지 않습니다.

<!-- CARROT:AUTO:BEGIN CruiseGapLevels -->
<!-- CARROT:AUTO:SOURCE facts="41532882d98ca07be179060d01184f79e5a1f393e0e242aca478a07205d15cc6" semantic="0b2beba3c4ae3136707b59ae19b20a500b34caf419dd7fc699481622c446c9e1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 4단계 (`4`)
- **범위:** 2단계 (`2`) ~ 4단계 (`4`)
- **변경 단위:** `1`
- **선택지:** `2` 2단계, `3` 3단계, `4` 4단계
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseGapLevels -->

<!-- CARROT:MANUAL:BEGIN CruiseGapLevels -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CruiseGapLevels -->

<!-- CARROT:SETTING:END CruiseGapLevels -->
