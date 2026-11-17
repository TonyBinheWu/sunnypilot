<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 저속 요구 추종·응답 기록

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 저속 요구 추종·응답 기록

`LowSpeedSteerReserve`

현대/기아 CAN-FD 토크 제어 전용. 0.30초 지속 요구 후 30 km/h 이하에서 필요한 출력만 최대 409까지 제공하고 30–40 km/h에서 감쇠합니다. 켜면 전 속도에서 공장 기본 비율과 증가/감소율을 사용하며 수동 값은 보존합니다. 관찰 기록은 한계를 높이지 않습니다. 실차 검증 필요.

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="e26e990d1e50d087e2af48802a2beaa679a5966b5e17187000fdb235fc28297d" semantic="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" reviewed-at="2026-11-17T12:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

현대/기아 CAN-FD 토크 조향에만 적용됩니다. 기본 한계 부근의 요구가 0.30초 지속되면 ≤30 km/h에서 필요한 만큼만 최대 409까지 허용하며 30–40 km/h에서 한계를 감쇠하고 ≥40 km/h에서 공장 기본 한계를 사용합니다. 켜진 동안 모든 속도에서 공장 기본 비율과 명령 증가/감소율을 사용합니다. 저장된 CustomSteerMax 및 CustomSteerDelta 값은 덮어쓰지 않고 실행 중에만 무시합니다. 제어 계수와 실시간 토크 학습은 유지되며 각도 제어 차량의 권한은 늘리지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

선택 스위치는 CustomSteerMax 바로 아래에 있으며 약 0.5초 안에 읽으므로 재시작이 필요 없습니다. 끄면 저장된 수동 한계를 복원합니다. 장치 > 조향 학습 진행 및 웹/APK > 도구 > 조향 학습 진행에서 요구/전송 명령, 목표/실제 핸들 각도, 실제 각속도, 제한 원인, 좌우 명령 중 관찰 최대값을 확인합니다. 실시간 상태는 2초 뒤 만료 표시되며 저장된 통계는 과거 기록으로 표시하고 같은 차량/제어 방식에만 복원합니다. 켜진 상태의 통계만 로컬에 수집하고 60초 간격과 제어/기능 종료 시 저장하며 위치, 경로 또는 클라우드 전송은 포함하지 않습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

운전자 개입, CAN 무효, 조향 오류, 후진/정지, 모델 만료 또는 횡제어 해제 시 추가 자격을 취소합니다. 출력 회수는 공장 변화율을 따르며 EPS 요청 보호와 Panda 안전 제한을 유지합니다. 명령 단위는 Nm가 아닌 CAN 값이며 증가/감소 값은 핸들 각속도가 아닌 10 ms당 CAN 명령 변화량입니다. 관찰 최대값과 각도 오차는 물리 EPS 한계를 식별하지 않으며 한계를 높이거나 한계 시험에 사용하지 않습니다. 데스크톱 테스트만 완료했으며 실차 검증이 필요합니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
