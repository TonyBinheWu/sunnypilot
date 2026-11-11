<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_LIMIT" param="AutoRoadSpeedAdjust" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AutoRoadLimitSpeedAdjust (50)%

**Menu:** Driving \> Speed & Decel \> Speed Limit

---

<!-- CARROT:SETTING:BEGIN AutoRoadSpeedAdjust -->
<a id="AutoRoadSpeedAdjust"></a>

## AutoRoadLimitSpeedAdjust (50)%

`AutoRoadSpeedAdjust`

-1: set roadlimitspeed, 100: new road speed, 50: median, 0: not change

<!-- CARROT:AUTO:BEGIN AutoRoadSpeedAdjust -->
<!-- CARROT:AUTO:SOURCE facts="f18aae93bc45f89f0d9b8c492adc8ef7aa5f41c4898eed9d4094727b02349bd8" semantic="c5639d7240a075f5e1e1594a87177824bc3d8bf0192fbf8b3dc2b51a26ea762a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `-1%` ~ `100%`
- **Step:** `10`
- **Display unit:** `%`
- **Menu:** Driving \> Speed & Decel \> Speed Limit
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoRoadSpeedAdjust -->

<!-- CARROT:MANUAL:BEGIN AutoRoadSpeedAdjust -->
<!-- CARROT:REVIEW reviewed-for="c5639d7240a075f5e1e1594a87177824bc3d8bf0192fbf8b3dc2b51a26ea762a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `-1` — Immediately follows the new road-limit-based target when the road speed limit changes.
- `0` — Keeps the existing cruise set speed.
- `1`–`99` — Blends the existing set speed with a newly reduced road limit; higher values move closer to the new limit.
- `100` — Applies the newly reduced road limit directly.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the new target speed and transition timing on the same section where the road speed limit changes.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoRoadSpeedAdjust -->

<!-- CARROT:SETTING:END AutoRoadSpeedAdjust -->
