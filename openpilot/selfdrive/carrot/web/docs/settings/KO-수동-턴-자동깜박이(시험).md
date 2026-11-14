<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="ManualTurnIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 수동 턴 자동깜박이(시험)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN ManualTurnIndicator -->
<a id="ManualTurnIndicator"></a>

## 수동 턴 자동깜박이(시험)

`ManualTurnIndicator`

운전자의 조향력과 핸들 회전, 실제 차체 회전을 함께 확인해 좌·우 턴의 깜박이를 켭니다. ATC 설정과 독립적으로 동작하며 차선이 흐린 교차로에서도 감지합니다. 시작 속도 5~60km/h, 같은 방향 조향력 0.15초, 조향각 42도 이상 및 22도 이상 증가, 같은 방향 차체 회전 조건을 확인합니다. 핸들 ±15도 복귀와 회전 안정화 또는 운전자 반대 조향으로 종료하며 최대 30초 유지합니다. 기본 꺼짐. 아이오닉5 PE의 지원 깜박이 장치와 자동 깜박이 제어 1·2번에서 동작합니다. 주차장 코너에서도 켜질 수 있으며 도로 곡선·회피 동작의 오점등 가능성과 실차 점등 검증이 남아 있습니다. 수동 차선변경 표시 중 같은 방향의 수동 턴 조건이 충족되면 기존 요청을 이어받아 턴 종료까지 추적합니다.

<!-- CARROT:AUTO:BEGIN ManualTurnIndicator -->
<!-- CARROT:AUTO:SOURCE facts="491428b06239c2ab55b4e9365e2a17bd741c375c8f24119418ace5c763cf1d0f" semantic="e08aa7e7e006ddb909a0060571a3f7983d6c70f1249f7f29cc42c19e87f3451a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualTurnIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualTurnIndicator -->
<!-- CARROT:REVIEW reviewed-for="e08aa7e7e006ddb909a0060571a3f7983d6c70f1249f7f29cc42c19e87f3451a" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

운전자의 같은 방향 조향력과 핸들 각도 증가, 신선한 차체 회전을 함께 확인해 턴을 표시합니다. ATC 설정과 횡제어 활성 여부에 관계없이 동작하며, 램프 피드백은 자동조향 요청에서 차단합니다.

핸들 복귀와 회전 안정화로 종료하고 반대 방향으로 직접 조향하면 취소합니다. 입력 오류와 설정 끄기도 요청을 종료합니다.
다음 수동 턴은 직전 표시의 마지막 유지 시점에서 2초가 지나고 양쪽 램프가 연속 1초 꺼진 뒤 새로 감지합니다. 두 조건은 동시에 확인합니다.
수동 차선 지시 중 같은 방향 수동 턴 조건이 충족되면 기존 요청과 확인 응답을 유지하며 턴 완료 조건으로 추적합니다. 새 탭 요청이 아닙니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

Git Pull 후 콤마를 재시작하고 이 옵션을 켭니다. 아이오닉5 PE의 지원 깜박이 장치와 자동 깜박이 제어 1·2번에서 사용합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

주차장 통로·경사로·주차 진입도 감지될 수 있습니다. 차선이 흐린 곡선과 회피 동작의 오점등 가능성이 남아 있으며 실차 점등 검증이 필요합니다.

[한국어 동작 조건](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/lane-change.md)
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END ManualTurnIndicator -->

<!-- CARROT:SETTING:END ManualTurnIndicator -->
