<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="AutoNaviSpeedDecelRate" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NaviSpeedDecelRate 0.01m/s^2x(120)

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedDecelRate -->
<a id="AutoNaviSpeedDecelRate"></a>

## NaviSpeedDecelRate 0.01m/s^2x(120)

`AutoNaviSpeedDecelRate`

Used to calculate the deceleration curve when approaching cameras and speed bumps. The stored value is multiplied by 0.01 m/s², so 120 means 1.2 m/s². Lower values start slowing farther away; higher values start closer. Updating the software does not change an existing saved setting.

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:AUTO:SOURCE facts="43420bb5ce296dc2a10a14a43092f5322fec680780d62dfd6ac0d53108d2690c" semantic="dd424d47dfc026837af962b9c56209e7643717b0eba2e3136437850b8bdd30c3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `120`
- **Range:** `50` ~ `300`
- **Step:** `10`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedDecelRate -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:REVIEW reviewed-for="f8c301abb791623a5f1ff08eb2caea713c2ab3040a02a6f6035af09687c06afa" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The lower the value, the further away it decelerates.

- **Higher:** Decelerates more strongly over a shorter distance.
- **Lower:** Starts farther away with gentler deceleration.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time on the same speed limit and camera type, comparing deceleration start, completion point, and passing speed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedDecelRate -->

<!-- CARROT:SETTING:END AutoNaviSpeedDecelRate -->
