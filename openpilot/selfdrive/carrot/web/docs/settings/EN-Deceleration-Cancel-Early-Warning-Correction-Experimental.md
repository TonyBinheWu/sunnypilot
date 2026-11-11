<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviDecelCancelEarlyWarning" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Deceleration Cancel: Early Warning Correction \[Experimental\]

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<a id="VehicleNaviDecelCancelEarlyWarning"></a>

## Deceleration Cancel: Early Warning Correction \[Experimental\]

`VehicleNaviDecelCancelEarlyWarning`

Experimental; works only with the deceleration cancel request on. A stock-navigation enforcement warning usually starts about 6.1 m x the limit (km/h) before its camera (about 366 m at 60 km/h), but on some roads/cars it starts earlier (about 460 m at 60 km/h), so box, fixed and mobile-zone previews are not matched and the warning is treated as an undetected kind. When on, the far end of the matching window grows up to 1.35x so these warnings find their kind. WARNING: the wider window can attach a nearby mobile-camera (mobile enforcement zone) preview to the wrong warning. If 'Deceleration Cancel: Mobile Zone' is on or AutoNaviSpeedCtrlMode is 2 or lower (mobile zones ignored), a real enforcement camera's deceleration may, with low probability, be skipped. Always verify the behaviour on the road after enabling.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:AUTO:SOURCE facts="6698cb3136efe130c650538fe229419434a585d00cf6c94c4a4513c44481dc18" semantic="ca6595f1bd5ba33a43b5c946ad4d3a7cb99440c06da4c111043f7d1654d3b7c6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelEarlyWarning -->
<!-- CARROT:REVIEW reviewed-for="ca6595f1bd5ba33a43b5c946ad4d3a7cb99440c06da4c111043f7d1654d3b7c6" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

With the master cancellation setting enabled, this widens preview matching for unusually early enforcement warnings. Disabling uses the existing matching window.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Experimental. An incorrect nearby mobile-zone match can skip real enforcement deceleration; compare enabled and disabled matching on the affected vehicle.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelEarlyWarning -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelEarlyWarning -->
