<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_START" param="AlwaysLateral" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 상시 조향

**메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작

---

<!-- CARROT:SETTING:BEGIN AlwaysLateral -->
<a id="AlwaysLateral"></a>

## 상시 조향

`AlwaysLateral`

크루즈가 켜져있지 않아도 조향제어를 허용합니다. 시스템 시작 후 최초 입력 준비 확인 전에는 조향하지 않습니다. 한 번 통과하면 이 검사는 다시 차단하지 않으며 기존 주행 중 안전 처리는 유지됩니다. Tesla는 실제 정차 시에도 조향할 수 있으며, 저속 이동 중 조향 제한은 유지됩니다. 차량 CAN 확장이 있는 Tesla는 화면의 세 손가락 접촉마다 이 설정을 즉시 전환합니다. 실험 모드는 바뀌지 않습니다. 끄더라도 활성 크루즈의 조향까지 해제하지는 않습니다. 지속적인 CAN 제어기 오류 또는 반복되는 캐스퍼 전방 안전 시스템 오류가 확인되면 경고와 함께 상시 조향도 해제되며, 오류가 해소되기 전에는 다시 켤 수 없습니다. 0: 끄기, 1: 켜기

<!-- CARROT:AUTO:BEGIN AlwaysLateral -->
<!-- CARROT:AUTO:SOURCE facts="a12e05b19d05c7b0de5acfa20761d44df70a871dcf252ccf594a596c44f001a7" semantic="3f6deea9c6bbfe6632488bcb5dfc98a7d569ea9227268d6d99cf4f6fc8019ea0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AlwaysLateral -->

<!-- CARROT:MANUAL:BEGIN AlwaysLateral -->
<!-- CARROT:REVIEW reviewed-for="3f6deea9c6bbfe6632488bcb5dfc98a7d569ea9227268d6d99cf4f6fc8019ea0" reviewed-at="2026-11-09T00:00:00+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 전진 가능한 기어에서 조향 상태가 켜져 있으면, 크루즈가 꺼져 있거나 주행 중 브레이크로 크루즈가 해제되어도 조향을 계속할 수 있습니다.
- **꺼짐:** 주행 제어가 활성 상태일 때만 조향할 수 있습니다.

이 설정은 조향과 크루즈의 활성 상태를 분리할 뿐이며 가속과 제동에는 영향을 주지 않습니다.
지원되는 Tesla 차량은 전진 가능한 기어에서 조향 상태가 이미 켜져 있으면 실제 정차 중에도 조향할 수 있습니다. 저속 이동 중 최소 조향 속도 제한은 유지되며, 조향 고장이나 조향 꺼짐 상태에서는 조향하지 않습니다.

시스템 시작 후 모델·차량 파라미터·자세 정보 등 필수 입력의 최초 준비 확인 전에는 조향하지 않습니다. 한 번 통과하면 이 시작 검사는 종료되며, 이후 입력의 일시적 불량이나 조향 해제·재작동으로 다시 차단하지 않습니다. 기존 주행 중 안전 처리는 유지됩니다. 초기 대기시간 만료만으로는 준비를 통과하지 않습니다.
지속적인 CAN 제어기 오류 또는 반복되는 캐스퍼 전방 안전 시스템 오류가 확인되면 경고와 함께 상시 조향도 해제되며, 오류가 해소되기 전에는 다시 켤 수 없습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 시작부터 조향을 사용하되 크루즈는 수동으로만 켜려면 `AutoEngage=1`, `AlwaysLateral=1`, `AutoCruiseControl=0`을 사용합니다. 변경 후 다음 주행에서 크루즈가 꺼진 상태와 주행 중 브레이크를 밟은 상태의 조향 동작을 각각 확인합니다.
차량 CAN 확장이 있는 Tesla는 화면의 세 손가락 접촉마다 이 설정을 즉시 전환합니다. 다음 접촉 전 손을 떼어야 하며 유지·중복 눌림은 반복 전환하지 않습니다. 실험/Chill 모드와 확인 상태는 바꾸지 않고 확인도 필요하지 않습니다. 업그레이드 시 기존 저장값은 유지합니다. 비상 해제용 조작이 아닙니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 이 설정만으로 조향을 켜지는 않습니다. `AutoEngage` 또는 차량 버튼으로 조향 상태가 먼저 켜져 있어야 합니다.
<!-- CARROT:NOTICE:END -->

완전히 정차하지 않았더라도 차량별 최소 조향 속도 이하에서는 조향이 중지될 수 있습니다. 조향 고장, 전진할 수 없는 기어, 차량 버튼이나 취소 버튼 설정으로 조향 상태가 꺼진 경우에도 조향하지 않습니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AlwaysLateral -->

<!-- CARROT:SETTING:END AlwaysLateral -->
