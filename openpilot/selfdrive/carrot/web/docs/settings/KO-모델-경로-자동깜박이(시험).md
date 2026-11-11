<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_LANECHANGE" param="ModelPathIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 모델 경로 자동깜박이(시험)

**메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)

---

<!-- CARROT:SETTING:BEGIN ModelPathIndicator -->
<a id="ModelPathIndicator"></a>

## 모델 경로 자동깜박이(시험)

`ModelPathIndicator`

30km/h 이상에서 모델의 1~3초 경로가 차선 곡선을 넘어 이어지고 실제 제어 곡률도 같은 방향이면 깜박이를 표시합니다. 대상 차선 신뢰도 10% 이상, 연속적인 경계와 반복 관측이 필요합니다. 좌측 중앙선·우측 로드에지 제외 조건을 적용하며 자동 조향 요청은 추가하지 않습니다. 기본 꺼짐. 아이오닉5 PE·Jetson USB2CAN 및 자동 깜박이 1·2번에서 지원합니다. 실제 램프와 주행 검증은 별도로 필요합니다.

<!-- CARROT:AUTO:BEGIN ModelPathIndicator -->
<!-- CARROT:AUTO:SOURCE facts="d0be245b9cd58348af40fd500c93c0b2d0a315b1c656c6e0d5a735c23a7fb7c8" semantic="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 차로 변경 (자동 턴)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelPathIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelPathIndicator -->
<!-- CARROT:REVIEW reviewed-for="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" reviewed-at="2026-11-01T04:38:46.044761+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

모델 경로와 곡선 차선을 같은 전방 위치에서 비교하여 지속적인 경계 횡단을 감지합니다. 대상 차선 신뢰도 10% 이상과 연속적인 기하·반복 관측·도로 곡률 대비 같은 방향의 제어가 필요합니다.

차선 재인식만으로 새 요청을 만들지 않으며 자동 조향 요청은 차단합니다. 넓은 갓길과 교차로 등에서는 경계 추정의 한계가 있습니다.
수동·모델 표시 요청이 보낸 짧은 원터치 피드백은 요청 시각·방향·레버 카운터가 일치할 때만 제한적으로 구분합니다. 반대 방향·레버 고정 조작·수신기의 운전자 개입 판정은 취소하며, 점등이 전송 완료 응답보다 먼저 보이면 짧게 기억한 뒤 일치하는 응답을 받아 유지합니다. 같은 방향을 아주 짧은 송신 구간에 직접 누른 경우에는 이 정보만으로 완전히 구별할 수 없습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelPathIndicator -->

<!-- CARROT:SETTING:END ModelPathIndicator -->
