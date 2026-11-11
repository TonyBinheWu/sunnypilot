<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviDecelCancelBox" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Deceleration Cancel: Box Camera

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelBox -->
<a id="VehicleNaviDecelCancelBox"></a>

## Deceleration Cancel: Box Camera

`VehicleNaviDecelCancelBox`

With the deceleration cancel request on, lets cruise + or a gas tap cancel the deceleration for a box-type (mobile camera housing, preview kind 2) camera.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelBox -->
<!-- CARROT:AUTO:SOURCE facts="cc785b565da1aa899ddaeb0273cf18046ff3a0de72ee5a0f9c98811fccfa2de1" semantic="42f846ee76666e7420105b1833d0fa4ff8f300b9c3d5efc820cd0fdc3d3d1eef" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `1`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelBox -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelBox -->
<!-- CARROT:REVIEW reviewed-for="42f846ee76666e7420105b1833d0fa4ff8f300b9c3d5efc820cd0fdc3d3d1eef" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

With the master cancellation setting enabled, enabling this item lets + or a gas tap cancel deceleration for box-camera enforcement. Disabling does not permit cancellation for this kind.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

A simultaneous fixed, signal or rear enforcement preview preserves that enforcement deceleration.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelBox -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelBox -->
