<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviSchoolZoneControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Stock Navigation 30 km/h Zone Limit

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSchoolZoneControl -->
<a id="VehicleNaviSchoolZoneControl"></a>

## Stock Navigation 30 km/h Zone Limit

`VehicleNaviSchoolZoneControl`

Applies only when external navigation is disconnected. While external navigation is connected, stock navigation is excluded even without a current guidance item. Cap the target speed at 30 km/h from a confirmed stock-navigation 30 km/h zone entry until the corresponding exit signal. This experimental control may also apply to non-school 30 km/h zones and is not yet supported on the PV5.

<!-- CARROT:AUTO:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:AUTO:SOURCE facts="f591b80f080c70a48041c51e8d5d54a82827a3c452df5adbe1d9fe4ad6492a06" semantic="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSchoolZoneControl -->
<!-- CARROT:REVIEW reviewed-for="15eb22197321d7512c27030134cd141a289a4cd2499931c4f1406a9fe2630761" reviewed-at="2026-09-13T07:52:39.874680+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

While external navigation is connected, it is used exclusively even without a current guidance item. After disconnection or receive timeout is detected, stock navigation resumes according to its settings.

When enabled, confirmed stock-navigation 30 km/h zones cap the target speed on supported vehicles. Disabling this setting removes this zone cap. It can also apply to non-school zones; PV5 is unsupported.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the external-navigation connection together with the displayed event type and remaining distance.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviSchoolZoneControl -->

<!-- CARROT:SETTING:END VehicleNaviSchoolZoneControl -->
