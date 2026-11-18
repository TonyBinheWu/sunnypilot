<!-- CARROT:GENERATED schema="1" locale="ko" group="SYS_NET" param="HotspotOnBoot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 부팅시 핫스팟켜기

**메뉴:** 시스템 \> 네트워크·지도

---

<!-- CARROT:SETTING:BEGIN HotspotOnBoot -->
<a id="HotspotOnBoot"></a>

## 부팅시 핫스팟켜기

`HotspotOnBoot`

USIM이 준비되고 이동통신 데이터가 연결되면 저장된 Wi-Fi 핫스팟을 자동으로 켜고 인터넷을 공유합니다. 수동 끄기는 이번 부팅 동안 자동 시작을 일시 정지합니다.

<!-- CARROT:AUTO:BEGIN HotspotOnBoot -->
<!-- CARROT:AUTO:SOURCE facts="1d52ce16a17fab84a2fc4f06123eeec4b1511523aaf94d0bb5cb7377174917e6" semantic="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 시스템 \> 네트워크·지도
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HotspotOnBoot -->

<!-- CARROT:MANUAL:BEGIN HotspotOnBoot -->
<!-- CARROT:REVIEW reviewed-for="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" reviewed-at="2026-11-18T09:30:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 SIM 준비와 최신 셀룰러 데이터 연결을 기다린 뒤 저장된 핫스팟과 인터넷 공유를 시작합니다. 끄면 이 설정이 자동 관리하던 핫스팟을 종료합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

업데이트 후 한 번 재시작하면 변경은 약 5초 이내에 적용됩니다. 기존 핫스팟 이름과 비밀번호를 유지하며, 다른 기기를 연결해 Carrot와 외부 인터넷 접속을 확인합니다. 시작 실패 시 간격을 두고 재시도합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

핫스팟을 수동으로 끄면 이 설정을 껐다 켜거나 기기를 재시작할 때까지 자동 시작을 일시 중지합니다. 셀룰러 일시 단절에도 로컬 연결은 유지합니다. 단일 Wi-Fi 무선 장치는 클라이언트에서 핫스팟으로 전환될 수 있으며, 요금제·APN·통신사가 테더링을 허용해야 합니다. APN이나 로밍 설정은 변경하지 않습니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HotspotOnBoot -->

<!-- CARROT:SETTING:END HotspotOnBoot -->
