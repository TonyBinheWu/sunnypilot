<!-- CARROT:GENERATED schema="1" locale="en" group="TESLA_FEATURES" param="TeslaAutoSpeedLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla Automatic Speed Wheel

**Menu:** Driving \> Tesla \> Tesla Features

---

<!-- CARROT:SETTING:BEGIN TeslaAutoSpeedLimit -->
<a id="TeslaAutoSpeedLimit"></a>

## Tesla Automatic Speed Wheel

`TeslaAutoSpeedLimit`

Default OFF; full restart required. On supported Tesla with additional vehicle CAN and alpha longitudinal control, follows the vehicle DAS speed limit while cruise and carrotpilot are engaged, adjusting set speed by 1 km/h or 1 mph per step. OFF omits automatic wheel output and its Panda permission; manual scrolling remains. Previously automatic activation now also requires this switch. Active navigation/Carrot speed control pauses it. Manual scrolling pauses it; scroll in opposite directions within one second or disengage/re-engage to resume. Existing braking, stale-input and missing-feedback protections remain. Not vehicle or road acceptance.

<!-- CARROT:AUTO:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:AUTO:SOURCE facts="caf5cff5f9b44ac3eb03975026e2657aa897c598cbddbdecc6b7a984e2656508" semantic="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Tesla \> Tesla Features
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoSpeedLimit -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoSpeedLimit -->
<!-- CARROT:REVIEW reviewed-for="911d5260e6889f09c0ae7b64773f4b55f394fc435d0c6b998249abe3deeb2be0" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

On supported Tesla with the additional vehicle CAN bus and alpha longitudinal control, adjusts the engaged cruise set speed toward the vehicle DAS limit one displayed unit at a time. OFF omits automatic wheel output and its Panda permission while retaining manual wheel input and other control paths. Navigation/Carrot speed control takes precedence; braking, stale input and missing acknowledgement retain their existing stops.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Enable the switch in the Tesla group and fully restart. Previously automatic installations must now opt in. Manual scrolling pauses adjustment; scroll in opposite directions within one second, or disengage and re-engage cruise, to resume.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

This follows the original vehicle speed limit and does not engage cruise. Software checks are not physical vehicle or road acceptance.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TeslaAutoSpeedLimit -->

<!-- CARROT:SETTING:END TeslaAutoSpeedLimit -->
