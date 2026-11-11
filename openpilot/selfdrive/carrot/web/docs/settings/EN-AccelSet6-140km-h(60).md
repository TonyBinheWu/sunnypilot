<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_ACCEL_TABLE" param="CruiseMaxVals6" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AccelSet6:140km/h(60)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table

---

<!-- CARROT:SETTING:BEGIN CruiseMaxVals6 -->
<a id="CruiseMaxVals6"></a>

## AccelSet6:140km/h(60)

`CruiseMaxVals6`

Acceleration from 140 km/h

<!-- CARROT:AUTO:BEGIN CruiseMaxVals6 -->
<!-- CARROT:AUTO:SOURCE facts="5ab6dbe844a938f277d6643b81525c9f72b2b26204dab75bb726efcc0e83ead3" semantic="2ef3b0ff9376edca155222806f33b84fd52d4ac09bcf4b0887d38f856e800145" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `60`
- **Range:** `1` ~ `250`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Speed Accel Table
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseMaxVals6 -->

<!-- CARROT:MANUAL:BEGIN CruiseMaxVals6 -->
<!-- CARROT:REVIEW reviewed-for="2ef3b0ff9376edca155222806f33b84fd52d4ac09bcf4b0887d38f856e800145" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Acceleration from 140 km/h.

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
<!-- CARROT:MANUAL:END CruiseMaxVals6 -->

<!-- CARROT:SETTING:END CruiseMaxVals6 -->
