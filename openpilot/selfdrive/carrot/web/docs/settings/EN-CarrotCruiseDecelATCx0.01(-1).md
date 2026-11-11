<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_CARROT" param="CarrotCruiseAtcDecel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CarrotCruiseDecelATCx0.01(-1)

**Menu:** Driving \> Cruise & Gap \> Carrot Cruise

---

<!-- CARROT:SETTING:BEGIN CarrotCruiseAtcDecel -->
<a id="CarrotCruiseAtcDecel"></a>

## CarrotCruiseDecelATCx0.01(-1)

`CarrotCruiseAtcDecel`

Carrot Cruise ATC Deceleration Setting, -1: Not Change

<!-- CARROT:AUTO:BEGIN CarrotCruiseAtcDecel -->
<!-- CARROT:AUTO:SOURCE facts="37748823016b1c2ce9df31383dc9c009c47d76a6ab10e44a812f9d7dca86f05d" semantic="a6733fcd86fb76d04b17b6518d26eb29a1989d9fad23e0faca06bbe22b4919a0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `-1`
- **Range:** `-1` ~ `200`
- **Step:** `10`
- **Menu:** Driving \> Cruise & Gap \> Carrot Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotCruiseAtcDecel -->

<!-- CARROT:MANUAL:BEGIN CarrotCruiseAtcDecel -->
<!-- CARROT:REVIEW reviewed-for="a6733fcd86fb76d04b17b6518d26eb29a1989d9fad23e0faca06bbe22b4919a0" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Carrot Cruise ATC Deceleration Setting.

- **Higher positive values:** Increase the maximum Carrot Cruise deceleration request during ATC.
- **Lower positive values:** Reduce the ATC deceleration limit.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On a supported vehicle and applicable drive mode, change one item at a time and check target speed and actual acceleration/deceleration requests.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> The current implementation applies only to ATC deceleration on supported Hyundai/Kia controllers. `-1` leaves the existing deceleration request unchanged.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CarrotCruiseAtcDecel -->

<!-- CARROT:SETTING:END CarrotCruiseAtcDecel -->
