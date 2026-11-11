<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_BUMP" param="AutoNaviSpeedBumpTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# SpeedBumpEndingPoint(1s)

**Menu:** Driving \> Speed & Decel \> Speed Bump

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpTime -->
<a id="AutoNaviSpeedBumpTime"></a>

## SpeedBumpEndingPoint(1s)

`AutoNaviSpeedBumpTime`

SpeedBumpEndingPoint(1s)

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpTime -->
<!-- CARROT:AUTO:SOURCE facts="44f608750f69bb09da4846b30d0334745b2959df13e974fd3e08e4f38ae8b9cf" semantic="7de62e4b1a3ae2d0795b55f526653d5513f930033333ce979280f28bc6580ffc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `1s`
- **Range:** `1s` ~ `50s`
- **Step:** `1`
- **Display unit:** `s`
- **Menu:** Driving \> Speed & Decel \> Speed Bump
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpTime -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpTime -->
<!-- CARROT:REVIEW reviewed-for="7de62e4b1a3ae2d0795b55f526653d5513f930033333ce979280f28bc6580ffc" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Uses remaining distance and current speed to calculate the speed-bump deceleration completion point.

- **Higher:** Uses a completion point farther before the speed bump.
- **Lower:** Uses a point closer to the speed bump.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use the same speed-bump section to verify the deceleration completion point and crossing speed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpTime -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpTime -->
