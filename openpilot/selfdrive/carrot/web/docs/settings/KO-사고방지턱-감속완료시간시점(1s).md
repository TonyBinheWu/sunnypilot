<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_BUMP" param="AutoNaviSpeedBumpTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 사고방지턱 감속완료시간시점(1s)

**메뉴:** 주행 제어 \> 속도·감속 \> 방지턱

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpTime -->
<a id="AutoNaviSpeedBumpTime"></a>

## 사고방지턱 감속완료시간시점(1s)

`AutoNaviSpeedBumpTime`

사고방지턱 감속완료시간시점(1s)

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpTime -->
<!-- CARROT:AUTO:SOURCE facts="3b7076e6ddca7de213a882a62f2284cb26e35364bd9d64d07b9dce67258ef663" semantic="7de62e4b1a3ae2d0795b55f526653d5513f930033333ce979280f28bc6580ffc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `1s`
- **범위:** `1s` ~ `50s`
- **변경 단위:** `1`
- **표시 단위:** `s`
- **메뉴:** 주행 제어 \> 속도·감속 \> 방지턱
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpTime -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpTime -->
<!-- CARROT:REVIEW reviewed-for="7de62e4b1a3ae2d0795b55f526653d5513f930033333ce979280f28bc6580ffc" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

방지턱까지 남은 거리와 현재 속도를 이용해 감속 완료 지점을 계산합니다.

- **값을 높이면:** 방지턱에서 더 먼 지점을 감속 완료 기준으로 사용합니다.
- **값을 낮추면:** 방지턱에 더 가까운 지점을 기준으로 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 방지턱 구간에서 감속 완료 지점과 방지턱 통과 속도를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpTime -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpTime -->
