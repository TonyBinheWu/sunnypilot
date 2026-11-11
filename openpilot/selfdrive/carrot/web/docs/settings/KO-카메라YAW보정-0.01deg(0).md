<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_CENTER" param="CameraYawTrimDeg" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 카메라YAW보정\*0.01deg(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 중앙 보정

---

<!-- CARROT:SETTING:BEGIN CameraYawTrimDeg -->
<a id="CameraYawTrimDeg"></a>

## 카메라YAW보정\*0.01deg(0)

`CameraYawTrimDeg`

카메라 좌우(YAW) 값을 미세조정(+: 오른쪽)

<!-- CARROT:AUTO:BEGIN CameraYawTrimDeg -->
<!-- CARROT:AUTO:SOURCE facts="d6c0eaa20936594e946aab2e8b6a0119adfe98bb62c0d2949634c7682d732449" semantic="290906bf88c0f6a12d995faeea4c0ab18dad803aefe18bf89e349b3a45474f4a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `-200` ~ `200`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 중앙 보정
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CameraYawTrimDeg -->

<!-- CARROT:MANUAL:BEGIN CameraYawTrimDeg -->
<!-- CARROT:REVIEW reviewed-for="290906bf88c0f6a12d995faeea4c0ab18dad803aefe18bf89e349b3a45474f4a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

카메라 좌우(YAW) 값을 미세조정(+: 오른쪽).

- **음수 방향:** 카메라 YAW를 왼쪽으로 보정합니다.
- **양수 방향:** 오른쪽으로 보정합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

평평하고 직선인 도로에서 일정한 속도로 확인하며, 한 단계씩 바꿔 좌우 편향이 줄어드는지 비교합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CameraYawTrimDeg -->

<!-- CARROT:SETTING:END CameraYawTrimDeg -->
