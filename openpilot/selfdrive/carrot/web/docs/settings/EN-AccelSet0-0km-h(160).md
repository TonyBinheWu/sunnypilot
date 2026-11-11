<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals0" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AccelSet0:0km/h(160)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals0 -->
<a id="CruiseMaxVals0"></a>

## AccelSet0:0km/h(160)

`CruiseMaxVals0`

Acceleration from 0 km/h to 10 km/h

<!-- CARROT:AUTO:BEGIN CruiseMaxVals0 -->
<!-- CARROT:AUTO:SOURCE facts="31ff58a30059c6d0e2bd975f126fd1dae9c4e3b73374dc21457548ef479e9443" semantic="10e4085bba3a9694e8a989ade4077d532afaa5245b9d72df8bcdfd397cb650f0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `160`
- **Range:** `1` ~ `250`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals0 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals0 -->
<!-- CARROT:REVIEW reviewed-for="10e4085bba3a9694e8a989ade4077d532afaa5245b9d72df8bcdfd397cb650f0" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Acceleration from 0 km/h to 10 km/h.

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
<!-- CARROT:MANUAL:END CruiseMaxVals0 -->

<!-- CARROT:SETTING:END CruiseMaxVals0 -->
