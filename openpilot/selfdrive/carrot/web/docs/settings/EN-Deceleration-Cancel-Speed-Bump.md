<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviDecelCancelBump" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Deceleration Cancel: Speed Bump

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelBump -->
<a id="VehicleNaviDecelCancelBump"></a>

## Deceleration Cancel: Speed Bump

`VehicleNaviDecelCancelBump`

With the deceleration cancel request on, lets cruise + or a gas tap cancel a stock-navigation speed-bump deceleration. The input is used only while the bump target (from AutoNaviSpeedBumpSpeed, AutoNaviSpeedBumpTime and AutoNaviSpeedDecelRate) is below the set speed, i.e. actually decelerating. The cancel applies to the nearest bump only.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:AUTO:SOURCE facts="8a2df07f8ce2bb4682437752222ff748c16c00f5631ae5a4eddd17e389df7766" semantic="ab15a94879c1067db343091913a6b8ee055f955c0564f0b44795d843826bedfd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `1`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelBump -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelBump -->
<!-- CARROT:REVIEW reviewed-for="ab15a94879c1067db343091913a6b8ee055f955c0564f0b44795d843826bedfd" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

With the master cancellation setting enabled, enabling this item lets + or a gas tap cancel deceleration for the nearest speed bump. Disabling does not permit cancellation for this kind.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

The input is used only when the computed bump target is below set speed and is actively reducing the target.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelBump -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelBump -->
