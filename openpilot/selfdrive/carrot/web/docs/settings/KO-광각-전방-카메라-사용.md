<!-- CARROT:GENERATED schema="1" locale="ko" group="SYS_CAMERA" param="UseWideCamera" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 광각 전방 카메라 사용

**메뉴:** 시스템 \> 카메라

---

<!-- CARROT:SETTING:BEGIN UseWideCamera -->
<a id="UseWideCamera"></a>

## 광각 전방 카메라 사용

`UseWideCamera`

기본값은 켜짐입니다. 광각 전방 카메라가 고장 난 장치에서만 끄세요. 끄면 camerad가 광각 카메라를 동기화 대상에서 제외하고 modeld가 일반 전방 카메라 영상을 두 입력에 재사용합니다. 카메라 화각과 모델 성능이 달라질 수 있습니다. 변경 후 기기를 재부팅하세요.

<!-- CARROT:AUTO:BEGIN UseWideCamera -->
<!-- CARROT:AUTO:SOURCE facts="665fdac7ed8e35177c50179944546b75d0b2731d89d0ce5d11be94bdc928a105" semantic="98f6143429525738b1a1748e10af5089802e78c1eeeb632ec050ee74ca08fd18" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `1`
- **범위:** `0` ~ `1`
- **메뉴:** 시스템 \> 카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseWideCamera -->

<!-- CARROT:MANUAL:BEGIN UseWideCamera -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END UseWideCamera -->

<!-- CARROT:SETTING:END UseWideCamera -->
