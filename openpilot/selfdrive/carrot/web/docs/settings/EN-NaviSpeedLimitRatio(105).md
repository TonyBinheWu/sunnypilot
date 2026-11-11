<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="AutoNaviSpeedSafetyFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NaviSpeedLimitRatio(105)%

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedSafetyFactor -->
<a id="AutoNaviSpeedSafetyFactor"></a>

## NaviSpeedLimitRatio(105)%

`AutoNaviSpeedSafetyFactor`

Reduce speed to the road speed limit\*set value at the speed camera

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedSafetyFactor -->
<!-- CARROT:AUTO:SOURCE facts="e51a7d0d140551cf553193598ea927587656cd60115ebb775feec587fbf815ad" semantic="eea3adb6e5ca418ecba31e8c96f61079f384473b7d7680324d8217bbc831c7c7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `105%`
- **Range:** `80%` ~ `120%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedSafetyFactor -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedSafetyFactor -->
<!-- CARROT:REVIEW reviewed-for="eea3adb6e5ca418ecba31e8c96f61079f384473b7d7680324d8217bbc831c7c7" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the target-speed ratio applied to camera and road speed limits.

- **Higher:** Raises the target relative to the speed limit.
- **Lower:** Lowers the target relative to the speed limit.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time on the same speed limit and camera type, comparing deceleration start, completion point, and passing speed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedSafetyFactor -->

<!-- CARROT:SETTING:END AutoNaviSpeedSafetyFactor -->
