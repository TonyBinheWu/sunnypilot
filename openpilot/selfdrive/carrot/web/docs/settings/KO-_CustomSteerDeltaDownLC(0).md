<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaDownLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerDeltaDownLC(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaDownLC -->
<a id="CustomSteerDeltaDownLC"></a>

## \_CustomSteerDeltaDownLC(0)

`CustomSteerDeltaDownLC`

(토크차량) 차선변경 시 일시적용 SteerDeltaDown ADAS ECU 연결 EV6 HDA2 토크형은 운전자 인계 시에도 10 ms당 3의 고정 감소율을 사용합니다.

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:AUTO:SOURCE facts="974e412e8f8d5f333a6531992f6103d468157a9dc9747b58dbfdeb1e0c0eccfd" semantic="24f993369a8dc843e97c8b377086b40d1cb55d05c6cdf714f2e9f859ab68ba73" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `50`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 조향 제한
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaDownLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:REVIEW reviewed-for="a336e35a09a15ab311502cba35f76a68aa166dc74ce982901b724dd1b69de65e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(토크차량) / 차선변경 시 일시적용 SteerDeltaDown.

- **값을 높이면:** 해당 조향 토크 한도 또는 변화율이 커집니다.
- **값을 낮추면:** 한도 또는 변화율이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원되는 토크 제어 차량에서 한 항목씩 조정하고, 정상 주행과 차선 변경에서 조향 증가·감소 속도를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 잘못된 값은 조향 또는 가감속의 안정성과 승차감을 떨어뜨릴 수 있습니다. 한 항목씩 작은 단계로 조정하고 이상이 있으면 기본값으로 복구합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSteerDeltaDownLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaDownLC -->
