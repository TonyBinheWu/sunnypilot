<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_START" param="AutoEngage" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 오토인게이지

**메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작

---

<!-- CARROT:SETTING:BEGIN AutoEngage -->
<a id="AutoEngage"></a>

## 오토인게이지

`AutoEngage`

주행시작시 자동 시작 1:조향ON, 2:조향ON + 크루즈 대기

<!-- CARROT:AUTO:BEGIN AutoEngage -->
<!-- CARROT:AUTO:SOURCE facts="f03382159d276206806a5bbe259e5c4fcf6cd9ea9a50e955bd3bc9f5ffe006a1" semantic="5d795f951b628b849d1157749c4b492dddea109419cdb315856d2246614b812e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoEngage -->

<!-- CARROT:MANUAL:BEGIN AutoEngage -->
<!-- CARROT:REVIEW reviewed-for="5d795f951b628b849d1157749c4b492dddea109419cdb315856d2246614b812e" reviewed-at="2026-08-23T10:46:56+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

이 설정은 주행을 시작할 때의 조향 상태와 크루즈 대기 상태를 정합니다. 실제 조향과 가속·제동을 즉시 시작하는 설정은 아닙니다.

- `0` — 조향 상태와 크루즈 대기 상태를 자동으로 켜지 않습니다.
- `1` — 조향 상태만 켭니다.
- `2` — 조향 상태를 켜고, 지원되는 차량에서는 크루즈 대기 상태도 켭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량을 안전하게 정차한 상태에서 변경하고 다음 주행에서 동작을 확인합니다.

| 원하는 동작 | 함께 사용할 설정 |
|---|---|
| 시작부터 조향, 크루즈는 수동 사용 | `AutoEngage=1`, `AlwaysLateral=1`, `AutoCruiseControl=0` |
| 시작부터 조향, 조건에 따라 크루즈 자동 활성화 | `AutoEngage=2`, `AlwaysLateral=1`, `AutoCruiseControl=1` |
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> `1` 또는 `2`를 선택해도 `AlwaysLateral=0`이면 크루즈가 비활성화된 동안에는 실제 조향이 작동하지 않습니다. 크루즈와 관계없이 조향하려면 `AlwaysLateral=1`이 함께 필요합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoEngage -->

<!-- CARROT:SETTING:END AutoEngage -->
