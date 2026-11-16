<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 저속 모델 조향 여유

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 저속 모델 조향 여유

`LowSpeedSteerReserve`

CAN-FD 토크 제어 전용. 30 km/h 이하에서 지속적인 요구가 있을 때 최대 409, 30–40 km/h에서 기본 한계로 복귀. 기본 토크 비율과 CustomSteerMax는 유지됩니다. 실차 검증 필요.

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="bfe3d8748db01453a4871c312a455dda38c963b2c89398d9663c23760e799a55" semantic="6a5d981658c4dd294c2fd535015e46b0fe4d8c3e9583fbe6b51bcf29586bdb4d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

현대/기아 CAN-FD 토크 조향에만 적용됩니다. 기존 한계에 가까운 요구가 0.30초 지속되면 30 km/h 이하에서 필요에 따라 최대 409까지 허용하며 30–40 km/h에서 원래 한계로 줄어듭니다. 일반 요구의 배율, 제어 계수와 학습값은 유지됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

CustomSteerMax 바로 아래의 선택적 스위치이며 처음에는 꺼져 있습니다. 약 0.5초 안에 다시 읽으므로 재시작은 필요 없습니다. CustomSteerMax를 덮어쓰지 않으며 기존 한계가 409 이상이면 추가 여유가 없습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

운전자 개입, 후진/정지, CAN 오류, 조향 고장, 누락되거나 오래된 모델 또는 횡제어 해제 시 추가 자격을 취소합니다. 기존 토크 변화율로 복귀하므로 즉시 사라지지는 않습니다. EPS 큰 각도 보호와 Panda 안전 제한은 유지됩니다. 데스크톱 테스트만 완료했으며 409와 속도 기준은 실차 검증된 능력이나 회전 완료 보장이 아닙니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
