<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AccelSet1:10km/h(160)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals1 -->
<a id="CruiseMaxVals1"></a>

## AccelSet1:10km/h(160)

`CruiseMaxVals1`

Acceleration from 10 km/h to 40 km/h

<!-- CARROT:AUTO:BEGIN CruiseMaxVals1 -->
<!-- CARROT:AUTO:SOURCE facts="5c75b64124b7083c07077b0315387c513c028082209f330593337c58c7d728bb" semantic="049a2f4d59b41e828fa48bb99c19bfa5060440ba1382f09e912dd397a5c1816d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `160`
- **Range:** `1` ~ `250`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals1 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals1 -->
<!-- CARROT:REVIEW reviewed-for="049a2f4d59b41e828fa48bb99c19bfa5060440ba1382f09e912dd397a5c1816d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Acceleration from 10 km/h to 40 km/h.

- **Higher:** Allows more maximum acceleration in this speed range.
- **Lower:** Makes acceleration gentler in this range.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one step at a time in the applicable speed range and check both acceleration to target speed and ride comfort.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseMaxVals1 -->

<!-- CARROT:SETTING:END CruiseMaxVals1 -->
