<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_FEEL" param="HkgPhase1Assist" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 현대·기아 4차종 조향·커브 보조

**메뉴:** 주행 제어 \> 차량 조향 \> 조향감

---

<!-- CARROT:SETTING:BEGIN HkgPhase1Assist -->
<a id="HkgPhase1Assist"></a>

## 현대·기아 4차종 조향·커브 보조

`HkgPhase1Assist`

EV6, Ioniq 5, Carnival, Sorento의 등록 플랫폼만 적용합니다. CAN-FD 토크 차량은 기존 저속 요구 추종(최대 409, 4/4)을 사용하고 저장된 수동 한계는 보존합니다. 각도 제어와 구형 Sorento는 추가 토크 없이 기존 한계를 유지합니다. 40–80 km/h부터 작은 곡률 수정을 부드럽게 하며 큰 요구는 더 빠르게 추종합니다. 직접 종방향 ACC 모드에서 신선한 모델의 연속 3프레임으로 전방 커브를 확인한 뒤 MPC 속도 상한을 낮춥니다. 기본 꺼짐. EPS/Panda 보호 유지, 긴급 회피·유턴·실차 성능 보장 없음. 저속에서 같은 방향 진입 요구의 기존 목표 필터 시정수를 최대 40% 줄입니다. 복귀·반전은 기존 필터를 유지하며 30–40 km/h에서 감쇠합니다. 저속 모델 목표 추종 개선은 차선 없는 모델 경로에만 적용하며 사용자 차선 계획 필터와 지연 보상은 유지합니다.

<!-- CARROT:AUTO:BEGIN HkgPhase1Assist -->
<!-- CARROT:AUTO:SOURCE facts="302e6748e18a7083e043a54f47220ff1b49e6ae80778ea24e113ed557167ade2" semantic="1c9c7c054bb743a7a9af0906faec089755f21f0f914e02d4a5b7addd3c56d7c2" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 조향감
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HkgPhase1Assist -->

<!-- CARROT:MANUAL:BEGIN HkgPhase1Assist -->
<!-- CARROT:REVIEW reviewed-for="1c9c7c054bb743a7a9af0906faec089755f21f0f914e02d4a5b7addd3c56d7c2" reviewed-at="2026-11-18T00:00:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

등록된 EV6, Ioniq 5, Carnival, Sorento 플랫폼에만 적용하며 기존 차종·HDA·토크/각도 판별을 유지합니다. 저속에서 같은 방향으로 커지는 진입 요구의 기존 목표 필터 시정수를 최대 40% 줄이고 30–40 km/h에서 원래 값으로 복귀합니다. 복귀와 반전은 원래 필터를 사용합니다. CAN-FD 토크 차량은 기존 LowSpeedSteerReserve의 자격 확인·토크 상한·변화율 보호도 재사용합니다. 각도 차량과 구형 Sorento의 실행기 권한은 늘리지 않습니다. 고속 소폭 곡률 수정에는 최대 0.08초 시정수의 추가 필터를 적용하고 큰 요구에는 필터를 줄입니다. 최종 곡률·실행기 제한은 그대로 적용됩니다.
저속 모델 목표 추종 개선은 차선 없는 모델 경로에만 적용하며 사용자 차선 계획 필터와 지연 보상은 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주차 상태에서 주행 제어 > 차량 조향 > 조향감에서 켜고 차량 구성별로 검증하십시오. 조향은 약 0.5초, 커브 보조는 약 1초마다 설정을 읽습니다. 저장된 수동 한계를 복원하려면 이 스위치와 LowSpeedSteerReserve를 모두 끄십시오. 저장값은 덮어쓰지 않으며 기존 저속 토크 경로에는 호환 Panda 펌웨어가 필요합니다. ACC 모드에서 직접 종방향·횡방향 제어가 모두 활성화되고 차량·제어·모델 데이터가 유효하며 연속 3개 새 모델 프레임이 있을 때만 커브 속도 상한을 적용합니다. 순정 ACC와 blended 모드는 바뀌지 않습니다. 최대 4초 근거리 모델 형상, 횡가속 목표 2.0 m/s²와 접근 감속 예산 1.2 m/s²를 사용하고 상한은 초당 최대 1.2 m/s 감소, 초당 0.5 m/s 해제됩니다. Carrot 속도 선택 뒤 MPC에 적용해 더 낮은 속도·정지 목표를 높이지 않으며 코스팅·선행차 가속 미리보기가 커브 감속을 완화하지 못하게 합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

페달·운전자 조향, CAN 무효, 조향 고장, 제어 비활성, 오래되거나 반복·재시작된 모델, 잘못된 형상은 커브 상한을 초기화합니다. 추가 커브 기능은 정지를 요청하지 않고 관찰 기록으로 EPS 능력을 추정하지 않습니다. EPS/Panda 보호·운전자 우선·요청 비트 보호·모델 파일·긴급 동작을 유지합니다. 데스크톱 시험은 실차 조종성·풀록/유턴·FSD 동등성을 입증하지 않습니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HkgPhase1Assist -->

<!-- CARROT:SETTING:END HkgPhase1Assist -->
