<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="ManualLaneChangeIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 수동 차선변경 깜박이(시험)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN ManualLaneChangeIndicator -->
<a id="ManualLaneChangeIndicator"></a>

## 수동 차선변경 깜박이(시험)

`ManualLaneChangeIndicator`

5km/h 이상에서 같은 방향의 조향을 0.15초 확인한 뒤, 힘을 풀거나 잠깐 반대 토크가 나와도 차선 접근이 계속되면 최근 의도를 최대 1.5초 기억합니다. 접근이 0.3초 넘게 멈추거나 0.15m 이상 복귀하면 취소하며 한 접근은 최대 4초만 추적합니다. 왼쪽은 최신 차량 카메라의 흰 차선 분류로 중앙선이 아님을 확인하며 노란 선·불명확하거나 오래된 분류는 차단합니다. 오른쪽은 넘으려는 차선부터 로드에지까지 현재·전방 모두 2.5m 이상 여유가 있어야 합니다. 바깥쪽 차선 인식 확률·옆 차로 폭·로드에지 표준편차는 조건으로 사용하지 않습니다. 넓은 갓길도 거리 조건을 만족할 수 있습니다. ATC·우회전 거리 옵션과 독립적이며 자동 조향은 요청하지 않습니다. 기본 꺼짐. 아이오닉5 PE·Jetson USB2CAN, 자동 깜박이 1·2번에서 지원합니다. 재요청은 최소 3초와 연속 1초 소등 후 새로운 조건에서 가능하고 자동 조향 피드백 보호는 최소 12초 유지합니다. 실제 차로 존재나 안전한 간격을 보장하지 않으며 변경 후 실차 검증은 별도로 필요합니다. 대상 차선 신뢰도 10% 이상을 확인한 접근만 시작하며, 이후 연속적인 접근은 최대 4초 추적합니다. 요청 후에는 완료·복귀·입력 오류 또는 최대 12초까지 유지 상태를 추적합니다. 순정 원터치 점멸의 즉시 소등은 보장하지 않습니다. 측정한 차선 접근 속도로 0.3초 뒤를 예측하여 점등 시점을 앞당깁니다. 차체 중심과 대상 경계의 거리 기준은 기존 0.9m에서 최대 1.2m까지만 앞당기며, 실제 0.15m 접근·운전자 의도·양쪽 경계의 일관된 이동 조건은 유지합니다.

<!-- CARROT:AUTO:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:AUTO:SOURCE facts="5b545ac8fa0a5c09a206ce61c7b294b919675a641082725f46d5b4d61feee8c0" semantic="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualLaneChangeIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:REVIEW reviewed-for="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" reviewed-at="2026-11-08T22:13:25+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

최근 운전자 조향 의도와 연속적인 차선 접근을 확인하여 표시합니다. 접근 시작 시 대상 차선 신뢰도 10% 이상을 확인하고, 좌측 중앙선·우측 로드에지 제외 조건을 적용합니다.

요청 후에는 완료·복귀·입력 오류를 추적하며 자동 조향 요청을 만들지 않습니다. 종료 요청 뒤에도 순정 원터치 점멸은 남을 수 있습니다.
측정한 차선 접근 속도로 0.3초 뒤를 예측하여 점등 시점을 앞당깁니다. 차체 중심과 대상 경계의 거리 기준은 기존 0.9m에서 최대 1.2m까지만 앞당기며, 실제 0.15m 접근·운전자 의도·양쪽 경계의 일관된 이동 조건은 유지합니다.

수동·모델 표시 요청이 보낸 짧은 원터치 피드백은 요청 시각·방향·레버 카운터가 일치할 때만 제한적으로 구분합니다. 반대 방향·레버 고정 조작·수신기의 운전자 개입 판정은 취소하며, 점등이 전송 완료 응답보다 먼저 보이면 짧게 기억한 뒤 일치하는 응답을 받아 유지합니다. 같은 방향을 아주 짧은 송신 구간에 직접 누른 경우에는 이 정보만으로 완전히 구별할 수 없습니다.
시속 5km부터 운전자가 옆 차선에 실제로 접근할 때 해당 방향의 깜빡이를 요청합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ManualLaneChangeIndicator -->

<!-- CARROT:SETTING:END ManualLaneChangeIndicator -->
