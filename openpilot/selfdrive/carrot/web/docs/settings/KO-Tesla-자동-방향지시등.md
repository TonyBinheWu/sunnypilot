<!-- CARROT:GENERATED schema="1" locale="ko" group="TESLA_FEATURES" param="TeslaAutoTurnSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla 자동 방향지시등

**메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능

---

<!-- CARROT:SETTING:BEGIN TeslaAutoTurnSignals -->
<a id="TeslaAutoTurnSignals"></a>

## Tesla 자동 방향지시등

`TeslaAutoTurnSignals`

차량 CAN과 실제 스토크가 있는 Model 3/Y: 회전 desire 시작 시 점등, 실측 방위·핸들 복귀로 완료. 확인된 회전만 신선한 허용 아래 정차 유지하며 차로변경 준비 점등은 유지합니다. 운전자 우선, 조향·출발 권한은 그대로입니다. 기본 꺼짐, 변경 후 재부팅 필요. 실차 검증 전 일반 도로에서 사용하지 마세요.

<!-- CARROT:AUTO:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:AUTO:SOURCE facts="9cd472dec07cc87709e961c1f807da47e76124aafa76097fbcd5632609971940" semantic="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoTurnSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:REVIEW reviewed-for="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" reviewed-at="2026-11-08T01:13:19.642100+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

회전 desire 시작 시 점등하며 준비나 거리만으로 켜지지 않습니다. 차로변경 준비 점등은 유지합니다. 완료는 신선한 실측 방위 20도·해당 방향 조향 30도 초과·1km/h 이상 이동 중 핸들 15도 이내 복귀로 판단합니다. 송신·점등을 확인한 회전만 신선한 횡방향 허용과 정상 자세 아래 정차 대기하며 새 요청·차로변경에는 적용하지 않습니다. 다음 cue는 현재 완료와 회전 desire를 기다리며 대기 상한은 3초입니다. 같은 방향 ID·60초 상한·반복마다 새 템플릿과 TX 에코·운전자 우선·취소/OFF 확인은 유지합니다. 피드백 상실은 종료하고 취소 미확인은 해당 주행을 차단합니다. PC 검증은 실제 지속 점등 증명이 아닙니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

기본 꺼짐이며 변경 후 재부팅합니다. 지원 Model 3/Y, 속도 휠과 공유하는 CAN1 확장선 감지(`0x3DF`), 신선한 실제 스토크 입력과 일치하는 Panda 펌웨어가 필요합니다. 수신된 CAN1 스토크를 우선하고 시간 초과·충돌 시 출력을 차단합니다. 램프 템플릿과 UI·실제 램프 피드백은 별도로 필요하며 App 요청도 기존 동작 완료까지 유지합니다. `blocked:*`, `waiting:*`는 화면 경고가 아닌 기록용 진단입니다. 조향·출발 권한은 늘리지 않습니다. 일반 도로 사용 전 해당 차량의 폐쇄 시험장에서 좌우 동작·고장·운전자 개입을 확인하세요. CAN 단절이나 장치 전원 상실 시 소등은 보장할 수 없습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

실행: `openpilot/selfdrive/car/tesla_turn_signals.py`. 의도: `openpilot/selfdrive/controls/lib/desire_helper.py`. 안전: `opendbc_repo/opendbc/safety/safety/safety_tesla_turn_signals.h`. 진단과 제한은 Tesla 사용자 가이드를 참고하세요.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaAutoTurnSignals -->

<!-- CARROT:SETTING:END TeslaAutoTurnSignals -->
