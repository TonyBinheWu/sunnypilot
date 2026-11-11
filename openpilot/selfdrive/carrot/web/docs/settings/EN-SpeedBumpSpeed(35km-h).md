<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_BUMP" param="AutoNaviSpeedBumpSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# SpeedBumpSpeed(35km/h)

**Menu:** Driving \> Speed & Decel \> Speed Bump

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpSpeed -->
<a id="AutoNaviSpeedBumpSpeed"></a>

## SpeedBumpSpeed(35km/h)

`AutoNaviSpeedBumpSpeed`

SpeedBumpSpeed(35km/h)

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpSpeed -->
<!-- CARROT:AUTO:SOURCE facts="9db567627367e563db89f441d66595da840f1ce5c07e0651b2aa63c6e3f845b8" semantic="f2f0361ff03c1cf9dab3e3e9dbbd9e6353118fe6de59f64759f708d81ec23587" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `35km/h`
- **Range:** `10km/h` ~ `100km/h`
- **Step:** `5`
- **Display unit:** `km/h`
- **Menu:** Driving \> Speed & Decel \> Speed Bump
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpSpeed -->
<!-- CARROT:REVIEW reviewed-for="f2f0361ff03c1cf9dab3e3e9dbbd9e6353118fe6de59f64759f708d81ec23587" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the target speed used for speed-bump deceleration.

- **Higher:** Raises the target crossing speed.
- **Lower:** Lowers the target crossing speed.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use the same speed-bump section to verify the deceleration completion point and crossing speed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpSpeed -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpSpeed -->
