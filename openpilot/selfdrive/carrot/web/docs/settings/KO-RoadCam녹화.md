<!-- CARROT:GENERATED schema="1" locale="ko" group="SYS_RECORD_BASIC" param="RecordRoadCam" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# RoadCam녹화

**메뉴:** 시스템 \> 녹화·전원 \> 녹화·전원

---

<!-- CARROT:SETTING:BEGIN RecordRoadCam -->
<a id="RecordRoadCam"></a>

## RoadCam녹화

`RecordRoadCam`

저장소에 비디오 녹화 0:녹화안함,1:일반카메라 2:일반카메라+광각카메라

<!-- CARROT:AUTO:BEGIN RecordRoadCam -->
<!-- CARROT:AUTO:SOURCE facts="649532970663a116c715887082c8273b9cdc86b1933a2e8b5091ee2a48195be2" semantic="ae86d8c67fad0c96a2cfaad63d1ccea6d5408fea17c62cd5a549ab67faf97d69" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 시스템 \> 녹화·전원 \> 녹화·전원
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RecordRoadCam -->

<!-- CARROT:MANUAL:BEGIN RecordRoadCam -->
<!-- CARROT:REVIEW reviewed-for="ae86d8c67fad0c96a2cfaad63d1ccea6d5408fea17c62cd5a549ab67faf97d69" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 녹화안함
- `1` — 일반카메라
- `2` — 일반카메라+광각카메라
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

저장 공간과 전원 조건을 확인한 뒤 설정하고, 다음 녹화 또는 오프로드 전환에서 결과를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 광각까지 녹화하면 저장 공간과 메모리 대역폭 사용량이 늘어납니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END RecordRoadCam -->

<!-- CARROT:SETTING:END RecordRoadCam -->
