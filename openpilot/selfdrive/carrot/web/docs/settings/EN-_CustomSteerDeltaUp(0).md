<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUp" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerDeltaUp(0)

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUp -->
<a id="CustomSteerDeltaUp"></a>

## \_CustomSteerDeltaUp(0)

`CustomSteerDeltaUp`

Torque Vehicle — Higher values increase steering wheel turn speed

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:AUTO:SOURCE facts="e95315163fe3d65994ece1be0ec7281357a262a959cdaa22c99ff165eec7bb48" semantic="22505d7f9d2fdc5441ecca4890ef75dd0dd73869c71f0347effa2d7f6d892664" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `50`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUp -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUp -->
<!-- CARROT:REVIEW reviewed-for="22505d7f9d2fdc5441ecca4890ef75dd0dd73869c71f0347effa2d7f6d892664" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Torque Vehicle — Higher values increase steering wheel turn speed.

- **Higher:** Increases the applicable steering-torque limit or rate.
- **Lower:** Reduces the limit or rate.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On supported torque-control vehicles, adjust one item at a time and verify steering ramp-up and ramp-down in normal driving and lane changes.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSteerDeltaUp -->

<!-- CARROT:SETTING:END CustomSteerDeltaUp -->
