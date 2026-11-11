<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_HYUNDAI" param="HyundaiCameraSCC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# HYUNDAI: CAMERA SCC

**메뉴:** 차량·하드웨어 \> 현대·기아

---

<!-- CARROT:SETTING:BEGIN HyundaiCameraSCC -->
<a id="HyundaiCameraSCC"></a>

## HYUNDAI: CAMERA SCC

`HyundaiCameraSCC`

1:롱컨차량 2:크루즈 상태 동기화 3:순정크루즈(CANFD롱컨배선) 꺼짐 상태에서 카메라 버스 SCC가 감지되면 CAN 오류 시 설정 활성화를 안내합니다. 이미 카메라 SCC가 적용된 차종은 제외합니다. CAN-FD CameraSCC에서 캐럿 롱컨과 코너레이더가 켜져 있으면, 정상 CAN·D단·브레이크 해제·시속 10.8km 초과 조건에서 꺼진 순정 SCC MAIN을 주기적으로 켜도록 요청합니다. AutoEngage와 캐럿 크루즈 활성 여부에 관계없이 적용하며, MAIN이 이미 켜져 있으면 이 경로의 추가 요청은 끝납니다. SET·재출발 요청에는 기존 캐럿 크루즈 활성 조건이 적용됩니다. CAN-FD CameraSCC에서 캐럿 롱컨을 사용하는 경우 계기판용 순정 SCC MAIN 상태와 캐럿의 활성 선택을 분리해 처리합니다. 조향 활성은 AutoEngage 초기 설정과 기존 운전자 버튼 설정을 따릅니다.

<!-- CARROT:AUTO:BEGIN HyundaiCameraSCC -->
<!-- CARROT:AUTO:SOURCE facts="706444b266fa0117d503db5bc3f6650d48b1dc128f39b1e700a631a998ef83d0" semantic="287a1e4a7254a0c59acf4e381efa7c629c34796276cbd8584241a52c4a779f28" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> 현대·기아
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HyundaiCameraSCC -->

<!-- CARROT:MANUAL:BEGIN HyundaiCameraSCC -->
<!-- CARROT:REVIEW reviewed-for="287a1e4a7254a0c59acf4e381efa7c629c34796276cbd8584241a52c4a779f28" reviewed-at="2026-11-04T12:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 이 설정으로 카메라 SCC를 강제하지 않습니다. 차종 기본 플래그와 다른 종방향 설정은 별도로 적용됩니다.
- `1` — 카메라 SCC 구성을 사용하고 오픈파일럿 종방향 제어를 활성화합니다.
- `2` — 크루즈 상태 동기화용으로 표시되며, 현재 차량 인터페이스에서는 `1`과 같이 카메라 SCC·롱컨을 활성화합니다.
- `3` — 카메라 SCC 배선을 사용하되 종방향 제어는 순정 크루즈에 맡깁니다.

설정이 꺼져 있고 카메라 SCC가 적용되지 않은 차량에서, 이번 onroad의 카메라 버스(bus2 또는 다중 Panda의 해당 버스)에 `SCC_CONTROL`(CAN-FD)이나 `SCC12`(일반 CAN) 수신 이력이 있으면 CAN 오류 시 **CameraSCC 설정을 켜 주세요** 안내가 표시됩니다. 설정을 자동 변경하지 않으며 기존 제어 해제와 진입 차단은 유지됩니다.
CAN-FD CameraSCC에서 캐럿 롱컨과 코너레이더가 켜져 있으면, 정상 CAN·D단·브레이크 해제·시속 10.8km 초과 조건에서 꺼진 순정 SCC MAIN을 주기적으로 켜도록 요청합니다. AutoEngage와 캐럿 크루즈 활성 여부에 관계없이 적용하며, MAIN이 이미 켜져 있으면 이 경로의 추가 요청은 끝납니다. SET·재출발 요청에는 기존 캐럿 크루즈 활성 조건이 적용됩니다.

CAN-FD CameraSCC에서 캐럿 롱컨을 사용하는 경우 계기판용 순정 SCC MAIN 상태와 캐럿의 활성 선택을 분리해 처리합니다. 조향 활성은 AutoEngage 초기 설정과 기존 운전자 버튼 설정을 따릅니다.

<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량 사양과 배선 구성을 확인한 뒤 정차 상태에서 설정하고, 다음 주행에서 SCC·차선 경고 동작을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 차종·연식·HDA 세대·하네스 위치가 일치하지 않으면 SCC 또는 종방향 제어가 잘못 동작할 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HyundaiCameraSCC -->

<!-- CARROT:SETTING:END HyundaiCameraSCC -->
