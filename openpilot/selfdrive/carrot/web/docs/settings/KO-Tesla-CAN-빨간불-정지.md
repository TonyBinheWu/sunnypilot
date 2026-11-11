<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_START" param="TeslaCanTrafficStop" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla CAN 빨간불 정지

**메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작

---

<!-- CARROT:SETTING:BEGIN TeslaCanTrafficStop -->
<a id="TeslaCanTrafficStop"></a>

## Tesla CAN 빨간불 정지

`TeslaCanTrafficStop`

기본 꺼짐, 변경 후 재시작. Tesla Model 3/Y의 활성 openpilot 종제어에서만 신선한 APP\_trafficControl 빨간불·126m 미만 정지선을 보조 정지 제약으로 사용합니다. 8바이트·미터 단위·비전 출처만 지원하며 6바이트 DAS\_road는 차단합니다. 초록불은 이 제약만 해제합니다. 늦은 빨간불은 제동 한계를 넘을 수 있고, 신호 상실·거리 불일치는 인계와 기존 soft-disable을 요청합니다. 모델·주변 차량·수동 정지는 유지됩니다. 실차 신호와 거리 기준을 확인하고 폐쇄 시험장에서 검증해야 하며 도로 사용 승인을 뜻하지 않습니다.

<!-- CARROT:AUTO:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:AUTO:SOURCE facts="13d1f4d9dff19151c8bb5b930803b89c92d692a931031b27001fb57d48310baf" semantic="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 시작 동작
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaCanTrafficStop -->

<!-- CARROT:MANUAL:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:REVIEW reviewed-for="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" reviewed-at="2026-11-08T01:13:19.659661+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 Model 3/Y의 활성 openpilot 종제어에서 정지를 보조하고 끄면 기존 동작을 유지합니다. 서로 다른 빨간불 3회·0.2초와 양의 126m 미만 정지선으로 ACC·blended 제약을 추가하며 같은 목표의 초록불 3회·0.5초로 이 제약만 해제합니다. CAN 정지 중 blended는 더 강한 모델 제동을 유지하며 ACC 정지 계산을 사용하고 해제 후 선택 모드로 돌아갑니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

변경 후 재시작합니다. 램프·데이터 공유·신호 보조와 별개이며 정확한 8바이트·미터 단위·비전 APP_trafficControl만 허용하고 6바이트 DAS_road는 차단합니다. 페달 개입 후 제어 해제·재진입과 새 표본이 필요하며 다른 차종은 무시합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

실차 CAN·진행 방향 관련성·임시 2m 정지 여유를 폐쇄 시험장에서 확인해야 합니다. 가까운 빨간불은 제동 능력을 넘을 수 있고 0.5초 신호 상실·목표 불일치는 인계와 최종 제어 해제인 soft-disable을 요청하므로 운전자가 제동해야 합니다. Panda 권한 추가나 도로 검증이 아닙니다. 상세: 소스 저장소 docs/user/ko/tesla.md.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaCanTrafficStop -->

<!-- CARROT:SETTING:END TeslaCanTrafficStop -->
