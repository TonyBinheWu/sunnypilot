<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviDecelCancelMobileZone" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Deceleration Cancel: Mobile Zone

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelMobileZone -->
<a id="VehicleNaviDecelCancelMobileZone"></a>

## Deceleration Cancel: Mobile Zone

`VehicleNaviDecelCancelMobileZone`

With the deceleration cancel request on, lets cruise + or a gas tap cancel the deceleration for a mobile enforcement zone (blue circle). Mobile zones decelerate only when AutoNaviSpeedCtrlMode is 3, so this is unused at mode 2 or lower.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:AUTO:SOURCE facts="6fee8eb40848bbba31e8a45004e37d4501c35bf42b5b75bf748e0e4ff1612a01" semantic="570b00e282ceb2973c52e7d7121aea5fd059e453aac9b714b972da032891c62e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `1`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelMobileZone -->
<!-- CARROT:REVIEW reviewed-for="570b00e282ceb2973c52e7d7121aea5fd059e453aac9b714b972da032891c62e" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

With the master cancellation setting enabled, enabling this item lets + or a gas tap cancel deceleration for mobile enforcement zones. Disabling does not permit cancellation for this kind.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Mobile-zone deceleration itself operates only in navigation deceleration mode 3.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelMobileZone -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelMobileZone -->
