<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_LIMIT" param="AutoRoadSpeedLimitOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# RoadSpeedLimitOffset(-1)

**Menu:** Driving \> Speed & Decel \> Speed Limit

---

<!-- CARROT:SETTING:BEGIN AutoRoadSpeedLimitOffset -->
<a id="AutoRoadSpeedLimitOffset"></a>

## RoadSpeedLimitOffset(-1)

`AutoRoadSpeedLimitOffset`

RoadLimitSpeed+Set Value, -1:Not Use

<!-- CARROT:AUTO:BEGIN AutoRoadSpeedLimitOffset -->
<!-- CARROT:AUTO:SOURCE facts="5e188808669952844a5f9f1025e2cf2f1d2d58ca7807b9f7650dc4ad44745428" semantic="4e35d5a4d2ce2702b10b336d7e982781e60ea48724b8f97f29540fa36a14137d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `-1km/h`
- **Range:** `-1km/h` ~ `100km/h`
- **Step:** `1`
- **Display unit:** `km/h`
- **Menu:** Driving \> Speed & Decel \> Speed Limit
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoRoadSpeedLimitOffset -->

<!-- CARROT:MANUAL:BEGIN AutoRoadSpeedLimitOffset -->
<!-- CARROT:REVIEW reviewed-for="4e35d5a4d2ce2702b10b336d7e982781e60ea48724b8f97f29540fa36a14137d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

RoadLimitSpeed+Set Value.

- **Higher:** Moves the correction in the positive direction.
- **Lower:** Moves it in the negative direction.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the new target speed and transition timing on the same section where the road speed limit changes.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `-1` disables road-speed-limit-based target calculation.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoRoadSpeedLimitOffset -->

<!-- CARROT:SETTING:END AutoRoadSpeedLimitOffset -->
