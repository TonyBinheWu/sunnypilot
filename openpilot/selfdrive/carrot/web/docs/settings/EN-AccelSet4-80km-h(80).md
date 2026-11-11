<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AccelSet4:80km/h(80)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals4 -->
<a id="CruiseMaxVals4"></a>

## AccelSet4:80km/h(80)

`CruiseMaxVals4`

Acceleration from 80 km/h to 110 km/h

<!-- CARROT:AUTO:BEGIN CruiseMaxVals4 -->
<!-- CARROT:AUTO:SOURCE facts="6f5379e553e9fe2cb63c3b95f9667e19a33c9a82c56ce455b864d9c993c564c8" semantic="16e9dff4d42f6574aceb681dbdd9e8a5c2375b0f618309fb416550a7722a5e13" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `80`
- **Range:** `1` ~ `250`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals4 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals4 -->
<!-- CARROT:REVIEW reviewed-for="16e9dff4d42f6574aceb681dbdd9e8a5c2375b0f618309fb416550a7722a5e13" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Acceleration from 80 km/h to 110 km/h.

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
<!-- CARROT:MANUAL:END CruiseMaxVals4 -->

<!-- CARROT:SETTING:END CruiseMaxVals4 -->
