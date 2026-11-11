<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviDecelCancel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Stock Navigation Deceleration Cancel Request

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancel -->
<a id="VehicleNaviDecelCancel"></a>

## Stock Navigation Deceleration Cancel Request

`VehicleNaviDecelCancel`

Applies only when external navigation is disconnected (stock-navigation CAN). When enabled, while engaged (above about 18 km/h) and one of the kinds enabled below is decelerating, one press of cruise + or a gas tap (accelerator pressed for under 0.4 s) cancels that deceleration. The input does not raise the set speed (neither +1 nor the gas-tap +10). The cancel applies to that one camera or bump; the next one decelerates again. Signal and rear cameras and section enforcement cannot be cancelled; fixed cameras only when their own detail toggle is on. Turn each kind (box camera, mobile zone, speed bump, fixed camera) on or off in the details.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:AUTO:SOURCE facts="2ea9ff9d3d2b513f85cc529218313ef6388c8f232473380a75aaf5ad52a382c0" semantic="b4932756ef27f4ad90176e3da43004bb00e3808dc92ffd2bff98e1c48d5fe10f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancel -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:REVIEW reviewed-for="b4932756ef27f4ad90176e3da43004bb00e3808dc92ffd2bff98e1c48d5fe10f" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When enabled, cruise + or a gas tap can cancel selected kinds of supported stock-navigation deceleration. When disabled, this cancellation input is unused. Fixed, signal and rear enforcement remain excluded.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Select eligible kinds in the child settings. An input consumed by cancellation does not also increase set speed.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancel -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancel -->
