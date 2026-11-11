<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CURVE" param="AutoCurveSpeedLowerLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AutoCurveSpeed LowerLimit(30)

**Menu:** Driving \> Speed & Decel \> Curve & Turn

---

<!-- CARROT:SETTING:BEGIN AutoCurveSpeedLowerLimit -->
<a id="AutoCurveSpeedLowerLimit"></a>

## AutoCurveSpeed LowerLimit(30)

`AutoCurveSpeedLowerLimit`

Curve Minimum Speed Setting

<!-- CARROT:AUTO:BEGIN AutoCurveSpeedLowerLimit -->
<!-- CARROT:AUTO:SOURCE facts="1d4bb4c3ea824f8685b585b9b01fcde230769f55421ece977bd626da7cf10d64" semantic="185888d940778f15492f4238006adf9ccc06f2ab8e488209936b2cf8bd099102" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `30km/h`
- **Range:** `10km/h` ~ `200km/h`
- **Step:** `10`
- **Display unit:** `km/h`
- **Menu:** Driving \> Speed & Decel \> Curve & Turn
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoCurveSpeedLowerLimit -->

<!-- CARROT:MANUAL:BEGIN AutoCurveSpeedLowerLimit -->
<!-- CARROT:REVIEW reviewed-for="185888d940778f15492f4238006adf9ccc06f2ab8e488209936b2cf8bd099102" reviewed-at="2026-09-11T13:36:03+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the target-speed floor for vision curves and route turns. Vision control applies this floor to the curve target before using remaining distance to calculate the current approach ceiling.

- **Higher:** Prevents even sharp curves from selecting a target below the higher floor.
- **Lower:** Allows a lower curve target speed.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Adjust this separately from the curve factor when a target-speed floor is needed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

This value does not guarantee a safe speed for the road. A high floor can prevent necessary slowing.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoCurveSpeedLowerLimit -->

<!-- CARROT:SETTING:END AutoCurveSpeedLowerLimit -->
