<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DM" param="MuteDoor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 도어감지안함

**메뉴:** 차량·하드웨어 \> 운전자 모니터링

---

<!-- CARROT:SETTING:BEGIN MuteDoor -->
<a id="MuteDoor"></a>

## 도어감지안함

`MuteDoor`

도어감지안함

<!-- CARROT:AUTO:BEGIN MuteDoor -->
<!-- CARROT:AUTO:SOURCE facts="8210252c35e1d2603d2c2f872be3c938d3823bf6c492e9b19cb64efa56cdbc2e" semantic="2e4b627828fbc876d79a4469748d14cb1cd2ea8824c9f737817ecc770bcaf8db" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 차량·하드웨어 \> 운전자 모니터링
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MuteDoor -->

<!-- CARROT:MANUAL:BEGIN MuteDoor -->
<!-- CARROT:REVIEW reviewed-for="2e4b627828fbc876d79a4469748d14cb1cd2ea8824c9f737817ecc770bcaf8db" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 문 열림 상태를 주행 차단 이벤트에 추가하지 않습니다.
- **꺼짐:** 문이 열리면 문 열림 이벤트를 발생시킵니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

정차 상태에서 변경하고, 다음 주행에서 운전자 모니터링과 차량 경고 상태를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 켜면 문 열림 상태가 주행 차단 이벤트에서 제외됩니다. 출발 전에 모든 문이 닫혔는지 직접 확인해야 합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MuteDoor -->

<!-- CARROT:SETTING:END MuteDoor -->
