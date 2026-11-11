<!-- CARROT:GENERATED schema="1" locale="ko" group="SYS_NET" param="HotspotOnBoot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 부팅시 핫스팟켜기

**메뉴:** 시스템 \> 네트워크·지도

---

<!-- CARROT:SETTING:BEGIN HotspotOnBoot -->
<a id="HotspotOnBoot"></a>

## 부팅시 핫스팟켜기

`HotspotOnBoot`

COMMA에 USIM을 장착한경우 핫스팟을 자동으로 켜주는 기능

<!-- CARROT:AUTO:BEGIN HotspotOnBoot -->
<!-- CARROT:AUTO:SOURCE facts="e644cd0d78ca06f5dc4e1471a510bc4394c4323b119bc9cef3552f9f6f564a02" semantic="f60b11ad1a9e01c9a2140827ce36a15ff5fc686b902d45a7c578afb846582f96" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 시스템 \> 네트워크·지도
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HotspotOnBoot -->

<!-- CARROT:MANUAL:BEGIN HotspotOnBoot -->
<!-- CARROT:REVIEW reviewed-for="f60b11ad1a9e01c9a2140827ce36a15ff5fc686b902d45a7c578afb846582f96" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 장치 부팅 후 사용 가능한 셀룰러 연결로 핫스팟 자동 시작을 요청합니다.
- **꺼짐:** 부팅 시 핫스팟을 자동으로 켜지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

네트워크 연결 상태에서 변경하고, 다음 연결 또는 지도 화면에서 적용 결과를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> USIM과 셀룰러 네트워크를 사용할 수 있는 장치에서만 자동 핫스팟 시작이 가능합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HotspotOnBoot -->

<!-- CARROT:SETTING:END HotspotOnBoot -->
