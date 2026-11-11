<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviDecelCancelUnknown" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Deceleration Cancel: Undetected Camera Kind \[Experimental\]

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancelUnknown -->
<a id="VehicleNaviDecelCancelUnknown"></a>

## Deceleration Cancel: Undetected Camera Kind \[Experimental\]

`VehicleNaviDecelCancelUnknown`

With the deceleration cancel request on, lets cruise + or a gas tap cancel the deceleration for a stock-navigation enforcement warning whose camera kind preview was not received or not understood (experimental). Because the kind is unknown it can include signal or speed cameras that send no preview, so this is off by default and must be turned on separately even with the master on. Not applied to warnings at 30 km/h or below (school and senior zones) or inside a section. If a signal, rear or fixed preview is matched after the cancel, that kind's rule applies.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:AUTO:SOURCE facts="35bd808da8245ab8867b8cb12fb941b772aa0e411bac45bb95e72e3fa527cb40" semantic="bc790dfd91a22232bbc47f0077d136baa937beae69d660870e3b370ffa0052a7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancelUnknown -->
<!-- CARROT:REVIEW reviewed-for="bc790dfd91a22232bbc47f0077d136baa937beae69d660870e3b370ffa0052a7" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

With the master cancellation setting enabled, enabling this item lets + or a gas tap cancel deceleration for enforcement warnings with missing or unrecognized kind previews. Disabling does not permit cancellation for this kind.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Unknown kinds can include real enforcement cameras. This experimental option excludes warnings at 30 km/h or below and section enforcement.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancelUnknown -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancelUnknown -->
