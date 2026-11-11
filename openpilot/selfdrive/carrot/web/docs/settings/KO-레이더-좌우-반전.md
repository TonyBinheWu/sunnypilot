<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_RADAR" param="RadarTrackFlip" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 레이더 좌우 반전

**메뉴:** 차량·하드웨어 \> 레이더

---

<!-- CARROT:SETTING:BEGIN RadarTrackFlip -->
<a id="RadarTrackFlip"></a>

## 레이더 좌우 반전

`RadarTrackFlip`

전방 레이더 트랙의 좌우 방향을 보정합니다. 0: 정상(기본값) 1: 좌우 위치와 횡속도 반전 SCC·코너레이더·비전에는 적용하지 않습니다. 선행차 선택과 레이더 표시 모두에 적용됩니다. 차종별 자동 반전은 없으며, 실제 좌우 불일치를 확인한 차량에서만 선택하세요. 변경 후 차량을 재시동하거나 기기를 재부팅하세요.

<!-- CARROT:AUTO:BEGIN RadarTrackFlip -->
<!-- CARROT:AUTO:SOURCE facts="620b44909d3bda4d9a6a9133ba69b256d50492245e8a93f0a8868b0791013ff9" semantic="943dbe7612241b525566748d4a0c0383a19f20e4a140a100fad0a061f818df64" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 정상 (`0`)
- **범위:** 정상 (`0`) ~ 좌우 반전 (`1`)
- **변경 단위:** `1`
- **선택지:** `0` 정상, `1` 좌우 반전
- **메뉴:** 차량·하드웨어 \> 레이더
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RadarTrackFlip -->

<!-- CARROT:MANUAL:BEGIN RadarTrackFlip -->
<!-- CARROT:REVIEW reviewed-for="bd236f17fd9177f84d830907b23c61d75e1e8216aac4ca4dfb3cc9e3d4460cb8" reviewed-at="2026-09-23T00:19:35.914787+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

정상은 전방 트랙의 좌표를 그대로 사용하고, 반전은 좌우 위치와 횡속도를 함께 반전합니다. 선행차 선택과 레이더 표시 모두에 적용하며 SCC·코너레이더·비전과 종거리·종속도는 변경하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

영상과 레이더의 좌우 불일치가 확인된 차량에서만 선택하세요. 차종별 자동 반전은 없으며, 변경 후 차량을 재시동하거나 기기를 재부팅하면 다음 OnRoad 시작부터 적용됩니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END RadarTrackFlip -->

<!-- CARROT:SETTING:END RadarTrackFlip -->
