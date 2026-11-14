<!-- CARROT:GENERATED schema="1" locale="ko" group="TESLA_FEATURES" param="TeslaAutoSpeedLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla 자동 속도 휠

**메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능

---

<!-- CARROT:SETTING:BEGIN TeslaAutoSpeedLimit -->
<a id="TeslaAutoSpeedLimit"></a>

## Tesla 자동 속도 휠

`TeslaAutoSpeedLimit`

기본 꺼짐, 변경 후 전체 재시작. 추가 차량 CAN과 alpha 종제어가 있는 지원 Tesla에서 크루즈·carrotpilot 작동 중 차량 DAS 제한속도에 맞춰 설정속도를 1km/h 또는 1mph씩 조절합니다. 끄면 자동 휠 송신과 해당 Panda 권한을 설정하지 않으며 수동 휠은 유지됩니다. 기존 자동 활성화도 이제 이 설정을 켜야 합니다. 내비·Carrot 속도 제어 중에는 일시 중지합니다. 수동 휠은 자동 조절을 중지하고 1초 안에 반대 방향까지 돌리거나 해제·재진입하면 재개합니다. 브레이크·오래된 입력·응답 없음 보호는 유지하며 실차·도로 검증을 뜻하지 않습니다.

<!-- CARROT:AUTO:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:AUTO:SOURCE facts="21990d6e31ba76522bbc4473851f2d11e118849e1dfeb8eedee1dabbf6b02b9a" semantic="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> Tesla 전용 \> Tesla 기능
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoSpeedLimit -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:REVIEW reviewed-for="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

추가 차량 CAN과 alpha 종제어가 있는 지원 Tesla에서 작동 중인 크루즈 설정속도를 원래 DAS 제한속도에 맞춰 표시 단위 한 단계씩 조절합니다. OFF는 자동 휠 송신과 해당 Panda 권한을 설정하지 않으며 수동 휠과 다른 제어 경로는 유지합니다. 내비/Carrot 속도 제어가 우선이고 제동·오래된 입력·응답 없음 보호를 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

Tesla 그룹에서 켠 뒤 전체 재시작합니다. 이전 자동 활성화 차량도 이제 명시적으로 켜야 합니다. 수동 휠 조작은 자동 조절을 멈추며, 1초 안에 반대 방향까지 돌리거나 크루즈를 해제·재진입하면 재개합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

차량 원래 제한속도를 따르며 크루즈를 자동으로 활성화하지 않습니다. 소프트웨어 검사는 실차/도로 검증이 아닙니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TeslaAutoSpeedLimit -->

<!-- CARROT:SETTING:END TeslaAutoSpeedLimit -->
