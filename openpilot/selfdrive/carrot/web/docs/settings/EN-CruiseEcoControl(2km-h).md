<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_CARROT" param="CruiseEcoControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CruiseEcoControl(2km/h)

**Menu:** Driving \> Cruise & Gap \> Carrot Cruise

---

<!-- CARROT:SETTING:BEGIN CruiseEcoControl -->
<a id="CruiseEcoControl"></a>

## CruiseEcoControl(2km/h)

`CruiseEcoControl`

Temporarily increases the target speed for fuel efficiency

<!-- CARROT:AUTO:BEGIN CruiseEcoControl -->
<!-- CARROT:AUTO:SOURCE facts="003641918254bf3f3a7340567fc69363e59a77712f44cf5d1d56cbd03dc7e364" semantic="246d47bc61ed89bbb5fb72086ee161e3d96147de49d94b9b9459f285b9fc06e3" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `2km/h`
- **Range:** `0km/h` ~ `10km/h`
- **Step:** `1`
- **Display unit:** `km/h`
- **Menu:** Driving \> Cruise & Gap \> Carrot Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseEcoControl -->

<!-- CARROT:MANUAL:BEGIN CruiseEcoControl -->
<!-- CARROT:REVIEW reviewed-for="246d47bc61ed89bbb5fb72086ee161e3d96147de49d94b9b9459f285b9fc06e3" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Temporarily increases the target speed for fuel efficiency.

- **Higher:** Allows a larger temporary target-speed increase for economy control.
- **Lower:** Reduces that increase.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On a supported vehicle and applicable drive mode, change one item at a time and check target speed and actual acceleration/deceleration requests.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseEcoControl -->

<!-- CARROT:SETTING:END CruiseEcoControl -->
