<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DM" param="DriverMonitoringEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 운전자 감시 사용 (예외 설정)

**메뉴:** 차량·하드웨어 \> 운전자 모니터링

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringEnabled -->
<a id="DriverMonitoringEnabled"></a>

## 운전자 감시 사용 (예외 설정)

`DriverMonitoringEnabled`

기본값은 켜짐이며 그대로 두는 것을 권장합니다. 이 예외 옵션은 DM 카메라가 없거나 고장 나서 정상 운전자 감시를 사용할 수 없는 장치를 위한 것입니다. 끄면 일반 주행의 DM 모델과 경고, 감시로 인한 강제 감속 및 재사용 제한이 비활성화됩니다. 운전자 감시 없이 운행하면 지역 법규, 차량 요건 또는 사용 조건을 위반할 수 있으므로 적용 요건과 안전 책임을 확인한 경우에만 끄세요.

<!-- CARROT:AUTO:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:AUTO:SOURCE facts="c37114f4ed11a229bdcffda403b464489a364743f7d815d73d22ad3f7f83ccc5" semantic="75de16e159e826f4dfe20f040bbaada4fc65960b24b5d45781569bb9bb118027" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `1`
- **범위:** `0` ~ `1`
- **메뉴:** 차량·하드웨어 \> 운전자 모니터링
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringEnabled -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END DriverMonitoringEnabled -->

<!-- CARROT:SETTING:END DriverMonitoringEnabled -->
