<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DEVICE" param="HardwareC3xLite" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# C3X Lite 하드웨어

**메뉴:** 차량·하드웨어 \> 기기 하드웨어

---

<!-- CARROT:SETTING:BEGIN HardwareC3xLite -->
<a id="HardwareC3xLite"></a>

## C3X Lite 하드웨어

`HardwareC3xLite`

C3X Lite에서만 켜세요. 스피커·앰프 대신 GPIO 부저를 사용하며 오디오·로그 기록 프로세스를 끕니다. 변경 후 기기를 재부팅하세요.

<!-- CARROT:AUTO:BEGIN HardwareC3xLite -->
<!-- CARROT:AUTO:SOURCE facts="6841aa6611662e1e618c4bba5ca28caf6d552074949c5e11a38c7b94058ea3f1" semantic="1d1f4a2f5d6f90a2445f2e04e4f643f09e565be8708d71ac3d2190980ba0455c" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 차량·하드웨어 \> 기기 하드웨어
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HardwareC3xLite -->

<!-- CARROT:MANUAL:BEGIN HardwareC3xLite -->
<!-- CARROT:REVIEW reviewed-for="1d1f4a2f5d6f90a2445f2e04e4f643f09e565be8708d71ac3d2190980ba0455c" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** C3X Lite에서만 켜세요. 스피커·앰프 대신 GPIO 부저를 사용하며 오디오·로그 기록 프로세스를 끕니다. 변경 후 기기를 재부팅하세요.
- **꺼짐:** 해당 기능을 적용하지 않고 기존 동작을 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

기기 하드웨어가 정확히 일치할 때만 변경하고, 재부팅 후 소리·기록·프로세스 상태를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 일반 장치에서 켜면 오디오와 로그 기록 프로세스가 비활성화될 수 있습니다. 변경 후 기기를 재부팅해야 합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HardwareC3xLite -->

<!-- CARROT:SETTING:END HardwareC3xLite -->
