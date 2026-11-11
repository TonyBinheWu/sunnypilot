<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="AutoNaviSpeedCtrlEnd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NaviSpeedEndingPoint(6s)

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedCtrlEnd -->
<a id="AutoNaviSpeedCtrlEnd"></a>

## NaviSpeedEndingPoint(6s)

`AutoNaviSpeedCtrlEnd`

Time until decel completes, based on speed x time

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedCtrlEnd -->
<!-- CARROT:AUTO:SOURCE facts="dde42662f579dbd3a44aa6c8d3cff598e14b8d5b4821ebff840408c289f67ba4" semantic="310d348eaca8548ab5ee44af0a5126ab993dcc4265cbb669485438b669022d38" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `6s`
- **Range:** `3s` ~ `20s`
- **Step:** `1`
- **Display unit:** `s`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedCtrlEnd -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedCtrlEnd -->
<!-- CARROT:REVIEW reviewed-for="310d348eaca8548ab5ee44af0a5126ab993dcc4265cbb669485438b669022d38" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the time basis for reaching the target speed before a camera or speed-limit point.

- **Higher:** Moves target-speed completion farther before the point and completes deceleration earlier.
- **Lower:** Reaches the target speed closer to the point.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time on the same speed limit and camera type, comparing deceleration start, completion point, and passing speed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedCtrlEnd -->

<!-- CARROT:SETTING:END AutoNaviSpeedCtrlEnd -->
