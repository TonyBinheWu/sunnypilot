<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_CANFD" param="CanfdDebug" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CANFD Debug(0)

**메뉴:** 차량·하드웨어 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdDebug -->
<a id="CanfdDebug"></a>

## CANFD Debug(0)

`CanfdDebug`

CANFD Debug(0)

<!-- CARROT:AUTO:BEGIN CanfdDebug -->
<!-- CARROT:AUTO:SOURCE facts="046ad302bb31bb3ac58f644e036febf34b7ebb66db318cbf09442f7154c05831" semantic="12eb933ab9caf967e2a49d1d4a6b0a39f236a64333398e155efc78871fd68181" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `-1` ~ `128`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdDebug -->

<!-- CARROT:MANUAL:BEGIN CanfdDebug -->
<!-- CARROT:REVIEW reviewed-for="12eb933ab9caf967e2a49d1d4a6b0a39f236a64333398e155efc78871fd68181" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

설정값을 현대·기아 CCNC CAN FD 메시지 생성기의 진단 모드로 전달합니다. 일반 사용자 기능이 아니며 값별 의미는 현재 사용자 규격으로 고정되어 있지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량의 HDA·CAN FD 구성을 확인한 뒤 정차 상태에서 설정하고, 다음 주행에서 관련 기능과 오류 유무를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 개발자 진단값이며 차량 CAN 메시지 생성에 직접 전달됩니다. 진단 목적이 아니면 기본값을 유지합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CanfdDebug -->

<!-- CARROT:SETTING:END CanfdDebug -->
