<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals5" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AccelSet5:110km/h(70)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals5 -->
<a id="CruiseMaxVals5"></a>

## AccelSet5:110km/h(70)

`CruiseMaxVals5`

Acceleration from 110 km/h to 140 km/h

<!-- CARROT:AUTO:BEGIN CruiseMaxVals5 -->
<!-- CARROT:AUTO:SOURCE facts="f6ef6ee6751afe778bdadfc536d35fd6c9966802956f936cc8465f618bb2d65b" semantic="a0f4ffd54b85589db8416339bd40445bb361ec457c039fe5e700bad5f7e4c5ae" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `70`
- **Range:** `1` ~ `250`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals5 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals5 -->
<!-- CARROT:REVIEW reviewed-for="a0f4ffd54b85589db8416339bd40445bb361ec457c039fe5e700bad5f7e4c5ae" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Acceleration from 110 km/h to 140 km/h.

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
<!-- CARROT:MANUAL:END CruiseMaxVals5 -->

<!-- CARROT:SETTING:END CruiseMaxVals5 -->
