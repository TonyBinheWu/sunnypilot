<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DEVICE" param="CommaPedalEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Comma Pedal사용

**메뉴:** 차량·하드웨어 \> 기기 하드웨어

---

<!-- CARROT:SETTING:BEGIN CommaPedalEnabled -->
<a id="CommaPedalEnabled"></a>

## Comma Pedal사용

`CommaPedalEnabled`

ACC 미 장착 차량에서 Comma Pedal 장치를 통한 종방향 제어를 허용합니다. CC\_ONLY\_CAR 차량에서만 사용할 수 있으며, 차량의 Cruise ready가 꺼져 있을 때에만 작동합니다. Cruise ready 상태에서는 순정 크루즈 컨트롤이 우선하여 Comma Pedal 제어를 사용할 수 없습니다.

<!-- CARROT:AUTO:BEGIN CommaPedalEnabled -->
<!-- CARROT:AUTO:SOURCE facts="48d199f4fb88442c56de6b6c8fd2c4e5e4159bbd6ace466b52ee0089d60d2554" semantic="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 차량·하드웨어 \> 기기 하드웨어
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CommaPedalEnabled -->

<!-- CARROT:MANUAL:BEGIN CommaPedalEnabled -->
<!-- CARROT:REVIEW reviewed-for="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" reviewed-at="2026-11-03T12:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

명시적인 페달 프로파일이 있는 CC_ONLY_CAR 차량에서 장치 CAN 수신과 안전 조건을 만족하면 페달 제어를 허용합니다. 현재 프로파일은 레이 EV용이며, 순정 Cruise ready·크루즈 활성·입력 오류·브레이크·운전자 가속 입력 시 페달 출력을 차단합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

설정은 차량·하드웨어 → 기기 하드웨어에 있습니다. 차량과 페달 장치의 프로파일을 확인한 뒤 설정하고 재부팅하여 차량 파라미터와 Panda 펌웨어 적용을 완료하세요.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

CarrotPilot 실차 작동과 제동·정차 유지 성능은 별도 검증이 필요합니다. 제출자가 보고한 가속 제한 증상은 아직 해결되지 않았습니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CommaPedalEnabled -->

<!-- CARROT:SETTING:END CommaPedalEnabled -->
