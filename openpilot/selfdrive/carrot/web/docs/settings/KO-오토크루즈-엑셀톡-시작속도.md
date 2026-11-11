<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_AUTOCRUISE" param="AutoGasTokSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 오토크루즈: 엑셀톡 시작속도

**메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈

---

<!-- CARROT:SETTING:BEGIN AutoGasTokSpeed -->
<a id="AutoGasTokSpeed"></a>

## 오토크루즈: 엑셀톡 시작속도

`AutoGasTokSpeed`

엑셀톡기능:가속페달을 톡 밟았다가 뗌 설정속도 이상에서 작동

<!-- CARROT:AUTO:BEGIN AutoGasTokSpeed -->
<!-- CARROT:AUTO:SOURCE facts="0a3f82d1945559fb8ae14904db0a3eda4eeedbd0cb0a66e1d6ad62cda30f013c" semantic="566c9988c19eba63fd6ef647f6a0e4a6d6ba01d071de04c633eb540cc2cf4441" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0km/h`
- **범위:** `0km/h` ~ `200km/h`
- **변경 단위:** `5`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasTokSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasTokSpeed -->
<!-- CARROT:REVIEW reviewed-for="566c9988c19eba63fd6ef647f6a0e4a6d6ba01d071de04c633eb540cc2cf4441" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

엑셀톡기능:가속페달을 톡 밟았다가 뗌 / 설정속도 이상에서 작동.

- **값을 높이면:** 적용되는 속도 또는 속도 기준이 높아집니다.
- **값을 낮추면:** 속도 또는 속도 기준이 낮아집니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 출발·가속 페달·선행차 조건에서 한 항목씩 변경하고, 크루즈 활성화 시점과 설정 속도를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasTokSpeed -->

<!-- CARROT:SETTING:END AutoGasTokSpeed -->
