<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="AutoNaviSpeedCtrlEnd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 과속카메라감속 완료 시간(6초)

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedCtrlEnd -->
<a id="AutoNaviSpeedCtrlEnd"></a>

## 과속카메라감속 완료 시간(6초)

`AutoNaviSpeedCtrlEnd`

감속종료시점을 설정합니다.

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedCtrlEnd -->
<!-- CARROT:AUTO:SOURCE facts="fa51616be3368923c7b9a9974c2de89afcba0f9e7e8f835dd9c82c1b1dc885bc" semantic="310d348eaca8548ab5ee44af0a5126ab993dcc4265cbb669485438b669022d38" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `6s`
- **범위:** `3s` ~ `20s`
- **변경 단위:** `1`
- **표시 단위:** `s`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedCtrlEnd -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedCtrlEnd -->
<!-- CARROT:REVIEW reviewed-for="310d348eaca8548ab5ee44af0a5126ab993dcc4265cbb669485438b669022d38" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

카메라·제한속도 지점에서 목표 속도에 도달할 기준 시간을 정합니다.

- **값을 높이면:** 목표 속도 도달 지점이 더 멀어져 감속을 일찍 완료합니다.
- **값을 낮추면:** 지점에 더 가까워진 뒤 목표 속도에 도달합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 제한속도와 같은 종류의 카메라 구간에서 한 항목씩 변경해 감속 시작·완료 지점과 통과 속도를 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedCtrlEnd -->

<!-- CARROT:SETTING:END AutoNaviSpeedCtrlEnd -->
