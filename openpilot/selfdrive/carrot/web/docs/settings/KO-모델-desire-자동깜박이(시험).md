<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="ModelDesireIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 모델 desire 자동깜박이(시험)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN ModelDesireIndicator -->
<a id="ModelDesireIndicator"></a>

## 모델 desire 자동깜박이(시험)

`ModelDesireIndicator`

모델 출력의 턴·차선변경 확률이 50% 이상이고 직진·반대 방향보다 우세한 상태를 반복 확인하면 깜박이를 표시합니다. 턴은 10km/h, 차선변경은 30km/h 이상이며 횡제어 활성 상태에서만 시작합니다. 자동 조향 요청은 추가하지 않습니다. 기본 꺼짐. 아이오닉5 PE·Jetson USB2CAN 및 자동 깜박이 1·2번에서 지원합니다. 실제 램프와 주행 검증은 별도로 필요합니다. 30km/h 이상에서는 모델의 가까운 두 미래 예측이 모두 같은 방향 차로변경을 65% 이상으로 가리키고, 실제 좌우 차선 위치도 그 방향으로 접근할 때 깜빡이를 요청할 수 있습니다. 차선에 접근하지 않는 예측만으로는 켜지지 않으며, 이 기능은 조향을 요청하지 않습니다. 예측으로 점등한 뒤 분기에서 차로 폭이 넓어져도 같은 방향 모델 의도와 진행이 확인되면 같은 요청을 유지합니다. 의도가 약해지거나 반대로 바뀌면 분기 유지가 끝나며, CANCEL은 즉시 유지 요청을 해제합니다. 모델 턴 점등은 같은 방향 조향각 15도 이상과 실제 차체 회전 3도/초 이상도 확인합니다. 턴 확률이 30% 미만으로 내려가고 조향각이 ±10도 안에서 0.4초 안정되면 주행 중 유지 요청을 종료합니다.

<!-- CARROT:AUTO:BEGIN ModelDesireIndicator -->
<!-- CARROT:AUTO:SOURCE facts="1a1198f8c98797645cdf1aafc9690a802ca23623c4d259f60dd1b6354fbfdd93" semantic="d73f84bcf6ba7064705bfb722d8a81eb4a2d19fa2936d3d3e21fe478a59c63b5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelDesireIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelDesireIndicator -->
<!-- CARROT:REVIEW reviewed-for="d73f84bcf6ba7064705bfb722d8a81eb4a2d19fa2936d3d3e21fe478a59c63b5" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

모델의 턴·차선변경 확률이 충분히 우세한 상태를 반복 확인하여 신호를 표시합니다. 횡제어 활성 상태에서 시작하며, 기존 ATC 동작을 바꾸거나 추가 조향 요청을 만들지 않습니다.

같은 방향의 다른 신호 원인이 생겨도 중복 누르기 없이 이어받습니다. 실차 점등과 검출률은 별도 확인이 필요합니다.
수동·모델 표시 요청이 보낸 짧은 원터치 피드백은 요청 시각·방향·레버 카운터가 일치할 때만 제한적으로 구분합니다. 반대 방향·레버 고정 조작·수신기의 운전자 개입 판정은 취소하며, 점등이 전송 완료 응답보다 먼저 보이면 짧게 기억한 뒤 일치하는 응답을 받아 유지합니다. 같은 방향을 아주 짧은 송신 구간에 직접 누른 경우에는 이 정보만으로 완전히 구별할 수 없습니다.

30km/h 이상에서는 모델의 가까운 두 미래 예측이 모두 같은 방향 차로변경을 65% 이상으로 가리키고, 실제 좌우 차선 위치도 그 방향으로 접근할 때 깜빡이를 요청할 수 있습니다. 차선에 접근하지 않는 예측만으로는 켜지지 않으며, 이 기능은 조향을 요청하지 않습니다.

예측으로 점등한 뒤 분기에서 차로 폭이 넓어져도 같은 방향 모델 의도와 진행이 확인되면 같은 요청을 유지합니다. 의도가 약해지거나 반대로 바뀌면 분기 유지가 끝나며, CANCEL은 즉시 유지 요청을 해제합니다.
모델 턴 점등은 같은 방향 조향각 15도 이상과 최신 실측 회전 3도/초 이상도 확인합니다. 주행 중 턴 확률이 30% 미만이고 조향각이 ±10도 안에서 0.4초 안정되면 기존 30도 최대각 조건에 도달하기 전에도 유지를 끝낼 수 있습니다.

B1 릴리스 5는 확인된 자체 탭 피드백이 점멸의 소등 구간에도 이어지는 것을 허용합니다. 탭 후 중립 피드백은 허용을 닫고 이후 레버 입력은 소유권을 취소합니다. 반대 램프·원시 운전자 입력·CAN 오류·임대 만료는 계속 취소 조건입니다. 소프트웨어 리플레이는 실차 유지·취소 검증이 아닙니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelDesireIndicator -->

<!-- CARROT:SETTING:END ModelDesireIndicator -->
