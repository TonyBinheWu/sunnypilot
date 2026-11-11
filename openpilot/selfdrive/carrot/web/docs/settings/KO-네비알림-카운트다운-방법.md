<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="AutoNaviCountDownMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 네비알림 카운트다운 방법

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN AutoNaviCountDownMode -->
<a id="AutoNaviCountDownMode"></a>

## 네비알림 카운트다운 방법

`AutoNaviCountDownMode`

외부 내비 연결 중에는 외부 내비 거리만, 미연결 시에는 순정 내비 거리를 사용합니다. 연결 상태가 바뀌면 이전 카운트다운을 초기화합니다. 0: 알림없음 1: 턴지점+속도 2: 턴지점+속도+방지턱

<!-- CARROT:AUTO:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:AUTO:SOURCE facts="d9e73548d8bb5459854a22192745dca370540f833eb7a8d8fc8e274865b257d7" semantic="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `2`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviCountDownMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:REVIEW reviewed-for="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" reviewed-at="2026-09-13T07:52:40.605976+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

외부 내비가 연결되어 있으면 외부 내비만 사용하며, 현재 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 연결 종료 또는 수신 시간 초과가 확인되면 순정 내비를 각 설정에 따라 다시 사용합니다.

0은 알림 없음, 1은 턴 지점과 속도 이벤트, 2는 방지턱까지 포함합니다. 외부 내비 연결 중에는 외부 거리만 사용하고 미연결 시에는 순정 거리를 사용하며, 연결 전환 시 이전 카운트다운을 초기화합니다. 감속 시작 시점이나 강도는 바꾸지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 내비 연결 상태와 화면의 이벤트 종류·남은 거리를 함께 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoNaviCountDownMode -->

<!-- CARROT:SETTING:END AutoNaviCountDownMode -->
