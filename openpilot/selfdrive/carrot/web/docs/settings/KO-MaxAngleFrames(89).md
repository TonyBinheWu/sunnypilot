<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_AUX" param="MaxAngleFrames" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# MaxAngleFrames(89)

**메뉴:** 차량·하드웨어 \> 차량 보조

---

<!-- CARROT:SETTING:BEGIN MaxAngleFrames -->
<a id="MaxAngleFrames"></a>

## MaxAngleFrames(89)

`MaxAngleFrames`

89 권장

<!-- CARROT:AUTO:BEGIN MaxAngleFrames -->
<!-- CARROT:AUTO:SOURCE facts="9424d9f101db6e32704e7fcba55f38568cdc6d2178988594ebded61fb3cff6b5" semantic="c21f5b2f6d919fcc7d07af6ad5fe3f43c01fc42b1a190dd097bbd44f74ebad29" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `89`
- **범위:** `80` ~ `100`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> 차량 보조
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MaxAngleFrames -->

<!-- CARROT:MANUAL:BEGIN MaxAngleFrames -->
<!-- CARROT:REVIEW reviewed-for="c21f5b2f6d919fcc7d07af6ad5fe3f43c01fc42b1a190dd097bbd44f74ebad29" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

큰 조향각에서 연속 조향 요청을 유지할 수 있는 프레임 수를 조정합니다.

- **값을 높이면:** 큰 조향각에서 조향 요청을 유지할 수 있는 프레임 수가 늘어납니다.
- **값을 낮추면:** EPS 고장 방지를 위해 조향 요청을 더 일찍 끊습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원 차량에서만 한 항목씩 변경하고, 다음 주행에서 조향 또는 순정 SCC 동작을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 차량 제어 방식과 일치하지 않는 값은 조향 또는 순정 SCC 동작을 바꿀 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MaxAngleFrames -->

<!-- CARROT:SETTING:END MaxAngleFrames -->
