<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_CANFD" param="CanfdBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CAN-FD SPAS 깜박이 사용(시험)

**메뉴:** 차량·하드웨어 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdBlinkerControl -->
<a id="CanfdBlinkerControl"></a>

## CAN-FD SPAS 깜박이 사용(시험)

`CanfdBlinkerControl`

ECAN의 SPAS1/2 규격과 운전자 입력이 확인되는 현대·기아·제네시스 CAN-FD 차량에서 콤마로 깜박이를 제어합니다. 기본 꺼짐이며 변경 후 재부팅해야 합니다. 선택하면 Jetson USB2CAN 깜박이 경로는 중지됩니다. 깜박이 요청 중 주차 ECU를 잠시 정지하고 종료 후 복구합니다. 기존 자동 깜박이 제어 단계가 적용되며 차종별 실차 확인이 필요합니다.

<!-- CARROT:AUTO:BEGIN CanfdBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="11f1458ec493209d651f5f8ef30328c05276d4450d1d5731c7b97c0055d6b5df" semantic="b9c8da21ba0961eca86e2eeeedd9232360297164deac532d95f215a0433ae12c" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 차량·하드웨어 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN CanfdBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CanfdBlinkerControl -->

<!-- CARROT:SETTING:END CanfdBlinkerControl -->
