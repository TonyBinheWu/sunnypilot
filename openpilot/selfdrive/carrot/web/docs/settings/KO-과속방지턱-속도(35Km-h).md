<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_BUMP" param="AutoNaviSpeedBumpSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 과속방지턱 속도(35Km/h)

**메뉴:** 주행 제어 \> 속도·감속 \> 방지턱

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpSpeed -->
<a id="AutoNaviSpeedBumpSpeed"></a>

## 과속방지턱 속도(35Km/h)

`AutoNaviSpeedBumpSpeed`

과속방지턱 속도(35Km/h)

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpSpeed -->
<!-- CARROT:AUTO:SOURCE facts="39e4bbf2a21e4a93eae69d3d3b7ae5e25c1957e402abf260912afa5bb38113c7" semantic="f2f0361ff03c1cf9dab3e3e9dbbd9e6353118fe6de59f64759f708d81ec23587" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `35km/h`
- **범위:** `10km/h` ~ `100km/h`
- **변경 단위:** `5`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 속도·감속 \> 방지턱
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpSpeed -->
<!-- CARROT:REVIEW reviewed-for="f2f0361ff03c1cf9dab3e3e9dbbd9e6353118fe6de59f64759f708d81ec23587" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

감속 제어가 방지턱 구간에 적용할 목표 속도를 정합니다.

- **값을 높이면:** 방지턱 목표 통과 속도가 높아집니다.
- **값을 낮추면:** 목표 통과 속도가 낮아집니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 방지턱 구간에서 감속 완료 지점과 방지턱 통과 속도를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpSpeed -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpSpeed -->
