<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_LIMIT" param="AutoRoadSpeedLimitOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 도로제한속도맞춤(-1)

**메뉴:** 주행 제어 \> 속도·감속 \> 제한속도

---

<!-- CARROT:SETTING:BEGIN AutoRoadSpeedLimitOffset -->
<a id="AutoRoadSpeedLimitOffset"></a>

## 도로제한속도맞춤(-1)

`AutoRoadSpeedLimitOffset`

도로제한속도 + 설정값 -1: 안함,

<!-- CARROT:AUTO:BEGIN AutoRoadSpeedLimitOffset -->
<!-- CARROT:AUTO:SOURCE facts="b2d36fe54f51f42828ffbff50e0034bf5881da4ea9f8775f3ac5c14e7884f040" semantic="4e35d5a4d2ce2702b10b336d7e982781e60ea48724b8f97f29540fa36a14137d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `-1km/h`
- **범위:** `-1km/h` ~ `100km/h`
- **변경 단위:** `1`
- **표시 단위:** `km/h`
- **메뉴:** 주행 제어 \> 속도·감속 \> 제한속도
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoRoadSpeedLimitOffset -->

<!-- CARROT:MANUAL:BEGIN AutoRoadSpeedLimitOffset -->
<!-- CARROT:REVIEW reviewed-for="4e35d5a4d2ce2702b10b336d7e982781e60ea48724b8f97f29540fa36a14137d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

도로제한속도 + 설정값.

- **값을 높이면:** 보정값이 양의 방향으로 이동합니다.
- **값을 낮추면:** 보정값이 음의 방향으로 이동합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

도로 제한속도가 바뀌는 동일 구간에서 새 목표 속도와 속도 변경 시점을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `-1`은 도로 제한속도 기반 목표값 계산을 사용하지 않습니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoRoadSpeedLimitOffset -->

<!-- CARROT:SETTING:END AutoRoadSpeedLimitOffset -->
