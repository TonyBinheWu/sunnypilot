<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviSectionAvgControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차량 내비 구간단속 평균속도 제어

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSectionAvgControl -->
<a id="VehicleNaviSectionAvgControl"></a>

## 차량 내비 구간단속 평균속도 제어

`VehicleNaviSectionAvgControl`

외부 내비가 연결되지 않았을 때만 적용합니다. 순정 내비 CAN 구간단속 중에는 평소처럼 구간 제한속도(× 안전계수)로 고정합니다. openpilot 작동 중이고 크루즈 설정 속도가 그보다 높을 때 크루즈 + 버튼을 한 번 누르거나 악셀톡을 하면 그 구간의 고정을 풀고, 구간 진입 후 평균속도가 구간 제한속도 이하로 유지되는 범위에서만 설정 속도까지 허용합니다. 정체 등으로 늦게 간 시간만 쓸 수 있고, 적립이 없으면 기존 제한과 같습니다. 이 입력은 설정 속도를 올리지 않습니다. 크루즈 - 버튼을 길게 누르면 설정 속도는 그대로 두고 다시 고정합니다(짧게 누르면 평소처럼 설정 속도를 내립니다). 구간이 끝나면 초기화됩니다. 종점 카메라는 약 2km 전 예고 후 지점 감속합니다. 구간 시작은 평균속도 신호가 켜진 시점으로 잡는 실험 기능입니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:AUTO:SOURCE facts="4ce8279f5ee08be1815918153260a7c2db71ec7a8911e7d07707c3939fda290c" semantic="279eeacf277d306a733765fc4b26354220278af698c6266e606d727260d2e3ec" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSectionAvgControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:REVIEW reviewed-for="279eeacf277d306a733765fc4b26354220278af698c6266e606d727260d2e3ec" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜도 구간단속 진입 시에는 기존 제한속도 상한을 유지합니다. 작동 중 설정속도가 상한보다 높을 때 + 또는 악셀톡으로 해제하면, 느리게 달려 확보한 시간 여유 안에서 설정속도까지 허용합니다. 끄면 기존 구간 상한을 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 내비가 없을 때 적용합니다. - 길게 누르기로 다시 고정하며 구간 종료 시 초기화합니다. 구간 진입 신호와 주행거리 추정에 의존하는 실험 기능이며 종점 지점단속 감속은 유지합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviSectionAvgControl -->

<!-- CARROT:SETTING:END VehicleNaviSectionAvgControl -->
