<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_START" param="DisableMinSteerSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 저속조향제한해제

**메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작

---

<!-- CARROT:SETTING:BEGIN DisableMinSteerSpeed -->
<a id="DisableMinSteerSpeed"></a>

## 저속조향제한해제

`DisableMinSteerSpeed`

저속조향이 안되는 차량 제한해제(SMDPS장착차량): 1

<!-- CARROT:AUTO:BEGIN DisableMinSteerSpeed -->
<!-- CARROT:AUTO:SOURCE facts="ac2bc13a20a3c8650d6460b46744669d06c6088f13b9d8fba48bbdd2b66344a7" semantic="1e8fdd77dce60e211fb436b62a63f37b43a57d55ab7b465a438ac1459fdc1ca3" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DisableMinSteerSpeed -->

<!-- CARROT:MANUAL:BEGIN DisableMinSteerSpeed -->
<!-- CARROT:REVIEW reviewed-for="1e8fdd77dce60e211fb436b62a63f37b43a57d55ab7b465a438ac1459fdc1ca3" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 차량 인터페이스가 제공한 최소 조향 속도를 `0`으로 바꿉니다.
- **꺼짐:** 차량별 최소 조향 속도를 그대로 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량을 안전하게 정차한 상태에서 변경하고, 다음 주행 시작 시 조향·크루즈 상태가 의도대로 전환되는지 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> SMDPS 등 저속 조향을 실제로 지원하는 차량에서만 사용합니다. 차량의 물리적·안전 제한 자체를 제거하는 기능은 아닙니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END DisableMinSteerSpeed -->

<!-- CARROT:SETTING:END DisableMinSteerSpeed -->
