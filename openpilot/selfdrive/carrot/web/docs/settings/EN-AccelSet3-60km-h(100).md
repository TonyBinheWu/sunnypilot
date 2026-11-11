<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AccelSet3:60km/h(100)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals3 -->
<a id="CruiseMaxVals3"></a>

## AccelSet3:60km/h(100)

`CruiseMaxVals3`

Acceleration from 60 km/h to 80 km/h

<!-- CARROT:AUTO:BEGIN CruiseMaxVals3 -->
<!-- CARROT:AUTO:SOURCE facts="7c5392dedb3f4d56d0cb57342abeb7eaf0c56b69935457c2893d4aae225e1783" semantic="4f57b387beb33a3e51f30a8d098f704fd6277f5c4e5b82981b748a8f5f432cc0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `1` ~ `250`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals3 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals3 -->
<!-- CARROT:REVIEW reviewed-for="4f57b387beb33a3e51f30a8d098f704fd6277f5c4e5b82981b748a8f5f432cc0" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Acceleration from 60 km/h to 80 km/h.

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
<!-- CARROT:MANUAL:END CruiseMaxVals3 -->

<!-- CARROT:SETTING:END CruiseMaxVals3 -->
