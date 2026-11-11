<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_BUMP" param="AutoNaviSpeedBumpEndDistance" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 방지턱 감속 조기 종료 거리(200cm)

**메뉴:** 주행 제어 \> 속도·감속 \> 방지턱

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpEndDistance -->
<a id="AutoNaviSpeedBumpEndDistance"></a>

## 방지턱 감속 조기 종료 거리(200cm)

`AutoNaviSpeedBumpEndDistance`

외부 내비 연결 중에는 외부 내비의 남은 거리만 기준으로 해제하며, 미연결 시에는 순정 내비 거리를 사용합니다. 차량 순정 내비 또는 Carrot Navi가 보낸 방지턱의 남은 거리가 이 값 이하가 되면 방지턱 감속 제한을 먼저 해제합니다. 저장값과 표시 단위는 cm이며 0은 수신 지점까지 유지합니다. 지도상 방지턱 위치가 실제 위치보다 뒤에 있을 때 통과 후 속도 복원이 늦는 현상을 보정합니다. 값을 너무 크게 설정하면 실제 방지턱 전에 가속할 수 있습니다.

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpEndDistance -->
<!-- CARROT:AUTO:SOURCE facts="2c45b9ce1af7914380e7bba802dce08bb208de460867f2da7bb0e69b93f7e7b8" semantic="1d2c29dce19e2a3851161d46ce76db89eb7be23e3f9b3b3c1be663a3e2b402c9" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `200cm`
- **범위:** `0cm` ~ `5000cm`
- **변경 단위:** `10`
- **표시 단위:** `cm`
- **메뉴:** 주행 제어 \> 속도·감속 \> 방지턱
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpEndDistance -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpEndDistance -->
<!-- CARROT:REVIEW reviewed-for="1d2c29dce19e2a3851161d46ce76db89eb7be23e3f9b3b3c1be663a3e2b402c9" reviewed-at="2026-09-13T07:52:40.688374+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

외부 내비가 연결되어 있으면 외부 내비만 사용하며, 현재 안내 항목이 없어도 순정 내비를 사용하지 않습니다. 연결 종료 또는 수신 시간 초과가 확인되면 순정 내비를 각 설정에 따라 다시 사용합니다.

양수를 높이면 방지턱에서 더 멀리 남았을 때 감속 제한을 해제하고, 낮추면 더 가까이에서 해제합니다. 0은 남은 거리가 없어질 때까지 유지합니다. 외부 내비 연결 중에는 외부 거리만 기준으로 하며, 제한 해제는 원래 속도에 즉시 도달한다는 뜻이 아닙니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 내비 연결 상태와 화면의 이벤트 종류·남은 거리를 함께 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpEndDistance -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpEndDistance -->
