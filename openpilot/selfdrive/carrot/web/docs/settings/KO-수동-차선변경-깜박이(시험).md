<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="ManualLaneChangeIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 수동 차선변경 깜박이(시험)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN ManualLaneChangeIndicator -->
<a id="ManualLaneChangeIndicator"></a>

## 수동 차선변경 깜박이(시험)

`ManualLaneChangeIndicator`

5km/h 이상에서 같은 방향의 조향을 0.15초 확인한 뒤, 힘을 풀거나 잠깐 반대 토크가 나와도 차선 접근이 계속되면 최근 의도를 최대 1.5초 기억합니다. 접근이 0.3초 넘게 멈추거나 0.15m 넘게 복귀한 상태가 0.15초 지속되면 취소하며 한 접근은 최대 4초만 추적합니다. 왼쪽은 최신 차량 카메라의 흰 차선 분류로 중앙선이 아님을 확인하며 노란 선·불명확하거나 오래된 분류는 차단합니다. 오른쪽은 넘으려는 차선부터 로드에지까지 현재·전방 모두 2.5m 이상 여유가 있어야 합니다. 바깥쪽 차선 인식 확률·옆 차로 폭·로드에지 표준편차는 조건으로 사용하지 않습니다. 넓은 갓길도 거리 조건을 만족할 수 있습니다. ATC·우회전 거리 옵션과 독립적이며 자동 조향은 요청하지 않습니다. 기본 꺼짐. 아이오닉5 PE·Jetson USB2CAN, 자동 깜박이 1·2번에서 지원합니다. 재요청은 최소 3초와 연속 1초 소등 후 새로운 조건에서 가능하고 자동 조향 피드백 보호는 최소 12초 유지합니다. 실제 차로 존재나 안전한 간격을 보장하지 않으며 변경 후 실차 검증은 별도로 필요합니다. 대상 차선 신뢰도 10% 이상을 확인한 접근만 시작하며, 이후 연속적인 접근은 최대 4초 추적합니다. 요청 후에는 완료·복귀·입력 오류 또는 최대 12초까지 유지 상태를 추적합니다. 순정 원터치 점멸의 즉시 소등은 보장하지 않습니다. 측정한 차선 접근 속도로 0.3초 뒤를 예측하여 점등 시점을 앞당깁니다. 차체 중심과 대상 경계의 거리 기준은 기존 0.9m에서 최대 1.2m까지만 앞당기며, 실제 0.15m 접근·운전자 의도·양쪽 경계의 일관된 이동 조건은 유지합니다. 차선 위치의 짧은 흔들림은 0.15초 확인하며, 복귀 중에는 새 점등을 보류합니다. 최근 조향 의도가 있고 양쪽 경계가 같은 방향으로 이동하며 차로 폭이 유지되면 제한된 위치 변화에서도 접근을 이어갑니다.

<!-- CARROT:AUTO:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:AUTO:SOURCE facts="0a909accfa21f5454ecf52202c3c0f9603979c014e2b82b9a270e560474efb03" semantic="d96432b8f8ff840459f65cab076ba12f6d57b1d333e585a4be25652182e1e7ba" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualLaneChangeIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:REVIEW reviewed-for="d96432b8f8ff840459f65cab076ba12f6d57b1d333e585a4be25652182e1e7ba" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

최근 운전자 조향 의도와 연속적인 차선 접근을 확인하여 표시합니다. 접근 시작 시 대상 차선 신뢰도 10% 이상을 확인하고, 좌측 중앙선·우측 로드에지 제외 조건을 적용합니다.

요청 후에는 완료·복귀·입력 오류를 추적하며 자동 조향 요청을 만들지 않습니다. 종료 요청 뒤에도 순정 원터치 점멸은 남을 수 있습니다.
측정한 차선 접근 속도로 0.3초 뒤를 예측하여 점등 시점을 앞당깁니다. 차체 중심과 대상 경계의 거리 기준은 기존 0.9m에서 최대 1.2m까지만 앞당기며, 실제 0.15m 접근·운전자 의도·양쪽 경계의 일관된 이동 조건은 유지합니다.

수동·모델 표시 요청이 보낸 짧은 원터치 피드백은 요청 시각·방향·레버 카운터가 일치할 때만 제한적으로 구분합니다. 반대 방향·레버 고정 조작·수신기의 운전자 개입 판정은 취소하며, 점등이 전송 완료 응답보다 먼저 보이면 짧게 기억한 뒤 일치하는 응답을 받아 유지합니다. 같은 방향을 아주 짧은 송신 구간에 직접 누른 경우에는 이 정보만으로 완전히 구별할 수 없습니다.
시속 5km부터 운전자가 옆 차선에 실제로 접근할 때 해당 방향의 깜빡이를 요청합니다.
경계 복귀가 0.15초 지속되어야 접근 추적을 취소하며, 복귀 중에는 새 점등을 보류합니다. 최근 운전자 의도와 차로 폭이 유지되는 양쪽 경계 이동이 확인되면 제한된 위치 변화에서도 접근을 이어갑니다.

B1 릴리스 5는 확인된 자체 탭 피드백이 점멸의 소등 구간에도 이어지는 것을 허용합니다. 탭 후 중립 피드백은 허용을 닫고 이후 레버 입력은 소유권을 취소합니다. 반대 램프·원시 운전자 입력·CAN 오류·임대 만료는 계속 취소 조건입니다. 소프트웨어 리플레이는 실차 유지·취소 검증이 아닙니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ManualLaneChangeIndicator -->

<!-- CARROT:SETTING:END ManualLaneChangeIndicator -->
