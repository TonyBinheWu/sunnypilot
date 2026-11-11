<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_CARROT" param="CruiseEcoControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 크루즈연비제어(2km/h)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈

---

<!-- CARROT:SETTING:BEGIN CruiseEcoControl -->
<a id="CruiseEcoControl"></a>

## 크루즈연비제어(2km/h)

`CruiseEcoControl`

HEV 차량의 EV모드 개입을 위해 일시적으로 목표 속도를 증가시킵니다.

<!-- CARROT:AUTO:BEGIN CruiseEcoControl -->
<!-- CARROT:AUTO:SOURCE facts="b168d938e8d92eff46cac6909d320408820384d7dfec8f45cdbe3423ed99cb5f" semantic="246d47bc61ed89bbb5fb72086ee161e3d96147de49d94b9b9459f285b9fc06e3" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `2km/h`
- **범위:** `0km/h` ~ `10km/h`
- **변경 단위:** `1`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseEcoControl -->

<!-- CARROT:MANUAL:BEGIN CruiseEcoControl -->
<!-- CARROT:REVIEW reviewed-for="246d47bc61ed89bbb5fb72086ee161e3d96147de49d94b9b9459f285b9fc06e3" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

HEV 차량의 EV모드 개입을 위해 일시적으로 목표 속도를 증가시킵니다.

- **값을 높이면:** 연비 제어가 일시적으로 올릴 수 있는 목표 속도 폭이 커집니다.
- **값을 낮추면:** 목표 속도 증가 폭이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원 차량과 해당 주행 모드에서 한 항목씩 변경하고, 목표 속도와 실제 가감속 요청을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseEcoControl -->

<!-- CARROT:SETTING:END CruiseEcoControl -->
