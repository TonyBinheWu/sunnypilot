<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_AUTOCRUISE" param="AutoCruiseControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 오토크루즈제어(HKG only)

**메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈

---

<!-- CARROT:SETTING:BEGIN AutoCruiseControl -->
<a id="AutoCruiseControl"></a>

## 오토크루즈제어(HKG only)

`AutoCruiseControl`

조건에 따라 자동으로 크루즈 ON(소프트홀드포함) 1:오토크루즈사용 2:소프트홀드 오류 발생 차량(스팅어등)

<!-- CARROT:AUTO:BEGIN AutoCruiseControl -->
<!-- CARROT:AUTO:SOURCE facts="a0dcec96bdbcb25a9147ce2705119f1e70ca6359d51e574459f1ca4228095d1f" semantic="686814b2afc5769591dcd6e77c8b4ea3b65cc4c23c4b4437b0e289a38f9273d5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoCruiseControl -->

<!-- CARROT:MANUAL:BEGIN AutoCruiseControl -->
<!-- CARROT:REVIEW reviewed-for="686814b2afc5769591dcd6e77c8b4ea3b65cc4c23c4b4437b0e289a38f9273d5" reviewed-at="2026-08-23T10:46:56+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

이 설정은 조건에 따라 크루즈의 가속·제동 제어를 자동으로 활성화합니다. 조향 상태를 직접 켜거나 조향 토크를 제한하지 않습니다.

- `0` — 자동 크루즈와 소프트홀드를 사용하지 않습니다. 수동 크루즈와 상시 조향은 그대로 사용할 수 있습니다.
- `1` — 자동 크루즈와 기본 소프트홀드를 사용합니다.
- `2` — 자동 크루즈를 사용하며, 기본 소프트홀드에서 오류가 발생하는 차량용 방식을 사용합니다.
- `3` — 현재 제어 코드에서는 `2`와 같은 자동 크루즈 및 소프트홀드 방식으로 동작합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

자동 크루즈가 필요 없으면 `0`, 일반적인 자동 크루즈는 `1`을 사용합니다. `2`는 `1`에서 소프트홀드 오류가 발생하는 차량에서만 사용하고, 같은 출발·가속 페달·선행차 조건에서 활성화 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `AlwaysLateral=1`이면 자동 크루즈가 꺼져도 조향 상태가 켜진 동안 조향을 계속합니다. `AlwaysLateral=0`이면 조향이 크루즈와 같은 활성 상태를 사용하므로 자동 크루즈가 켜지고 꺼질 때 조향도 함께 바뀌는 것처럼 보일 수 있습니다.
<!-- CARROT:NOTICE:END -->

이 설정은 현대·기아 차량용이며, 실제 사용 가능 여부는 차량의 종방향 제어 구성에 따라 달라집니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoCruiseControl -->

<!-- CARROT:SETTING:END AutoCruiseControl -->
