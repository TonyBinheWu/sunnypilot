<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_CARROT" param="CarrotCruiseDecel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CarrotCruiseDecel(-1)

**Menu:** Driving \> Cruise & Gap \> Carrot Cruise

---

<!-- CARROT:SETTING:BEGIN CarrotCruiseDecel -->
<a id="CarrotCruiseDecel"></a>

## CarrotCruiseDecel(-1)

`CarrotCruiseDecel`

Carrot Cruise Deceleration Setting, -1: Cruise OFF

<!-- CARROT:AUTO:BEGIN CarrotCruiseDecel -->
<!-- CARROT:AUTO:SOURCE facts="c0cbf76671180837a217d092d12d29833b29b2f94b5f050aca51db2efa769bb3" semantic="ba7e233d65895feac8118c77053f75720240197ed3ffa0ecf87ea2f953e899d2" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `-1`
- **Range:** `-1` ~ `200`
- **Step:** `10`
- **Menu:** Driving \> Cruise & Gap \> Carrot Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotCruiseDecel -->

<!-- CARROT:MANUAL:BEGIN CarrotCruiseDecel -->
<!-- CARROT:REVIEW reviewed-for="ba7e233d65895feac8118c77053f75720240197ed3ffa0ecf87ea2f953e899d2" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Carrot Cruise Deceleration Setting.

- **Higher positive values:** Increase the maximum Carrot Cruise deceleration request.
- **Lower positive values:** Reduce the allowed deceleration request.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On a supported vehicle and applicable drive mode, change one item at a time and check target speed and actual acceleration/deceleration requests.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> The current implementation applies only to supported Hyundai/Kia controllers. `-1` uses cruise disengagement instead of a Carrot Cruise deceleration request.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CarrotCruiseDecel -->

<!-- CARROT:SETTING:END CarrotCruiseDecel -->
