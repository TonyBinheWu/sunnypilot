<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_SCREEN" param="ShowDeviceState" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 디바이스정보 표시

**메뉴:** 화면 표시 \> 정보 표시

---

<!-- CARROT:SETTING:BEGIN ShowDeviceState -->
<a id="ShowDeviceState"></a>

## 디바이스정보 표시

`ShowDeviceState`

디바이스정보 표시

<!-- CARROT:AUTO:BEGIN ShowDeviceState -->
<!-- CARROT:AUTO:SOURCE facts="1b0205182858eaf6bd853e046a0d4112c44e3dfde6ef90ec634f5cad6a9a35d9" semantic="8a73859d7671881ac742cd8ff077a0351b890d70d1b91e02acafa07a24cebf7a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `1`
- **범위:** `0` ~ `1`
- **메뉴:** 화면 표시 \> 정보 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowDeviceState -->

<!-- CARROT:MANUAL:BEGIN ShowDeviceState -->
<!-- CARROT:REVIEW reviewed-for="8a73859d7671881ac742cd8ff077a0351b890d70d1b91e02acafa07a24cebf7a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 주행 HUD에 CPU 온도와 메모리 사용량 등 기기 상태를 표시합니다.
- **꺼짐:** 기기 상태 영역을 숨기고 HUD 정보 상자를 줄입니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

주행 화면에서 정보의 위치와 가독성을 확인하고, 필요한 정보만 표시되도록 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowDeviceState -->

<!-- CARROT:SETTING:END ShowDeviceState -->
