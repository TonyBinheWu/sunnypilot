<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AccelSet2:40km/h(120)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals2 -->
<a id="CruiseMaxVals2"></a>

## AccelSet2:40km/h(120)

`CruiseMaxVals2`

Acceleration from 40 km/h to 60 km/h

<!-- CARROT:AUTO:BEGIN CruiseMaxVals2 -->
<!-- CARROT:AUTO:SOURCE facts="caa4c9ef386a4abd2a0c5b51ee83769120c11e25f21d00751e98084b4f94322f" semantic="c060531fe2257a6fffdd9b0584198873e3bd3e85c69c0949ae84ab45a88bbabb" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `120`
- **Range:** `1` ~ `250`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals2 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals2 -->
<!-- CARROT:REVIEW reviewed-for="c060531fe2257a6fffdd9b0584198873e3bd3e85c69c0949ae84ab45a88bbabb" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Acceleration from 40 km/h to 60 km/h.

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
<!-- CARROT:MANUAL:END CruiseMaxVals2 -->

<!-- CARROT:SETTING:END CruiseMaxVals2 -->
