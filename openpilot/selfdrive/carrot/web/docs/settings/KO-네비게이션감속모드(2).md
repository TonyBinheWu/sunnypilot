<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="AutoNaviSpeedCtrlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 네비게이션감속모드(2)

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedCtrlMode -->
<a id="AutoNaviSpeedCtrlMode"></a>

## 네비게이션감속모드(2)

`AutoNaviSpeedCtrlMode`

0: 감속안함 1: 과속카메라 2: 과속카메라+과속방지턱 3: 과속카메라+과속방지턱+이동식카메라 순정 내비 CAN(VehicleNaviCanControl)의 이동식 단속 구간(내비 파란 원)도 이 값을 따릅니다. 3이면 감속하고, 2 이하이면 이동식 구간 경고를 무시합니다. 같은 경고에 고정식·신호·후면 카메라가 함께 있으면 항상 감속합니다.

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:AUTO:SOURCE facts="2a733038713a757b84b0f56dbf7431ab71f7a1a2669b4292e2f27c1e2eeef817" semantic="5b13349929a99c31fde786817313f0a97c7480cf55cdbce1da21739b3610e6d5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `2`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:REVIEW reviewed-for="5b13349929a99c31fde786817313f0a97c7480cf55cdbce1da21739b3610e6d5" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 감속안함
- `1` — 과속카메라
- `2` — 과속카메라+과속방지턱
- `3` — 과속카메라+과속방지턱+이동식카메라
지원하는 순정 내비 CAN 이동식 단속 구간도 이 설정을 따릅니다. 3에서 감속하며 2 이하에서는 이동식 구간 경고를 무시합니다. 고정식·신호·후면 단속이 함께 있으면 감속을 유지합니다.

<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 제한속도와 같은 종류의 카메라 구간에서 한 항목씩 변경해 감속 시작·완료 지점과 통과 속도를 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 선택한 이벤트의 거리와 제한속도가 내비 데이터로 들어올 때만 자동 감속이 작동합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:SETTING:END AutoNaviSpeedCtrlMode -->
