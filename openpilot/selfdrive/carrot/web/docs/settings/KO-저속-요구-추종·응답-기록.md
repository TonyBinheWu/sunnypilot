<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 저속 요구 추종·응답 기록

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## 저속 요구 추종·응답 기록

`LowSpeedSteerReserve`

현대/기아 CAN-FD 토크 전용. 0.30초 지속 요구 후 ≤30 km/h에서 필요한 출력만 최대 409, 명령 증가/감소율은 최대 4/4(10 ms당)까지 조정합니다. 30–40 km/h에서 감쇠하고 ≥40은 공장 기본 비율과 2/3을 사용합니다. 수동 값과 학습값은 보존하며 기록으로 한계를 높이지 않습니다. Panda 업데이트와 재시작 및 실차 검증이 필요합니다. 지원 EV6/Ioniq 5/Carnival/Sorento에서는 HkgPhase1Assist도 이 저속 경로를 켭니다. 저장된 수동 한계를 복원하려면 두 스위치를 모두 끄십시오. 2024년형 쏘렌토는 이 모드에서 순정 속도로 조향 토크를 높입니다. ADAS ECU 연결 EV6 HDA2 토크형에는 전용 2단 토크 한계와 기본 증가·감소율이 그대로 적용되며 선택 시 응답을 기록합니다.

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="16a3acc24c78f527956d5064d7bece2828196cdc1c3e7b752f710fc9b4071c02" semantic="590d03646724ca00ba438170b3d640523f2302c26f3eed63a702beb88e0b8aaa" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="05eafe68a23035bc4348334280884728605203a66ac88d3eaa2331b7d736becc" reviewed-at="2026-11-20T17:30:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

현대/기아 CAN-FD 토크 조향에만 적용됩니다. 기본 한계 부근 요구가 0.30초 지속되면 ≤30 km/h에서 최대 409까지 필요한 여유를 제공합니다. 허용된 요구 명령과 현재 출력의 차이에 따라 호스트 명령 증가/감소율을 공장 기본 2/3에서 10 ms당 최대 4/4 CAN 단위까지 조정하며 목표에 가까워지면 기본 변화율로 돌아갑니다. 30–40 km/h에서 토크 여유와 추가 변화율을 감쇠하고 정수 명령은 계단식으로 바뀌며 ≥40 km/h에서 공장 기본 비율과 변화율을 사용합니다.

저장된 CustomSteerMax 및 CustomSteerDelta는 덮어쓰지 않고 켜진 동안 공장 기본 정규화를 사용합니다. 끄면 수동 값을 복원하지만 Panda 제한을 넘는 명령은 차단됩니다. 제어 계수, 실시간 토크 학습값과 각도 제어 권한은 늘리지 않습니다.
2024년형 쏘렌토는 이 모드에서 순정 속도로 조향 토크를 높입니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주차 상태에서 업데이트한 뒤 재시작하여 새 Panda 펌웨어와 안전 파라미터를 읽어야 합니다. 선택 스위치는 CustomSteerMax 아래에 있으며 기본은 꺼짐입니다. 최초 업데이트 후에는 약 0.5초 안에 설정을 읽으므로 다시 시작할 필요가 없습니다. 장치 > 조향 학습 진행 및 웹/APK > 도구 > 조향 학습 진행에서 현재 명령, 선택된 변화율, 목표/실제 핸들 각도와 각속도, 제한 원인 및 좌우 명령 관찰 최대값을 확인합니다.

실시간 상태는 2초 뒤 만료됩니다. 과거 통계는 같은 차량/제어 방식에만 복원하고 로컬에서 60초 간격 또는 종료 시 저장하며 이 기록기는 위치, 경로 또는 클라우드 전송을 수집하지 않습니다.
지원 EV6/Ioniq 5/Carnival/Sorento에서는 HkgPhase1Assist도 이 저속 경로를 켭니다. 저장된 수동 한계를 복원하려면 두 스위치를 모두 끄십시오.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

운전자 개입, CAN 무효, 조향 오류, 후진/정지, 모델 만료 또는 횡제어 해제 시 추가 자격을 취소합니다. Panda는 독립적으로 수신한 신선한 CRC/카운터 검증 휠 속도와 운전자 데이터를 사용하며 누락되거나 만료된 입력은 추가 변화율을 허용하지 않습니다. 기존 112 단위/250 ms 실시간 한계, 요청 비트 및 운전자 양보 검사를 수신 주기 전달 명령에도 적용하며 운전자 개입 시 빠른 토크 해제를 유지합니다.

CAN 명령 변화율은 Nm 또는 실제 핸들 각속도가 아닙니다. 관찰 최대값은 물리 한계가 아니며 한계를 높이거나 시험하는 데 사용하지 않습니다. 데스크톱/네이티브 검사는 실차 능력을 증명하지 않습니다. [검증 범위와 기존 실패](https://github.com/TonyBinheWu/sunnypilot/blob/carrot-wip/docs/LOW_SPEED_STEERING_SAFETY.zh-TW.md)를 참고하세요.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
