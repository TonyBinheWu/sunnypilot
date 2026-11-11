<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_START" param="TeslaCanTrafficStop" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla CAN Red Light Stop

**Menu:** Driving \> Start & Auto \> Engage

---

<!-- CARROT:SETTING:BEGIN TeslaCanTrafficStop -->
<a id="TeslaCanTrafficStop"></a>

## Tesla CAN Red Light Stop

`TeslaCanTrafficStop`

Default OFF; restart required. Tesla Model 3/Y with active openpilot longitudinal control only: fresh APP\_trafficControl red and a stop line below 126 m supplement existing stops. Supports only the 8-byte, metre-scale, vision-backed profile; rejects 6-byte DAS\_road. Green releases only this constraint. Late red may exceed braking capability; lost/inconsistent signals request takeover and the existing soft-disable. Other obstacles and manual stops remain. Verify the vehicle protocol/distance reference and validate on a closed course; not road acceptance.

<!-- CARROT:AUTO:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:AUTO:SOURCE facts="eaca4d6bd2f28e2d2dd50a8805776aad81eed15ed488ef536d90f8cf32c66c32" semantic="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Start & Auto \> Engage
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaCanTrafficStop -->

<!-- CARROT:MANUAL:BEGIN TeslaCanTrafficStop -->
<!-- CARROT:REVIEW reviewed-for="046215718bed37d52f0c6633e5d551de2ff163be2a341b1cb647fab8b5f803dc" reviewed-at="2026-11-08T01:13:19.652113+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

ON supplements stops on Tesla Model 3/Y with active openpilot longitudinal control; OFF preserves existing behavior. Three unique red samples spanning 0.2 seconds and a positive line distance below 126 m admit a constraint in ACC or blended; green needs three same-target samples spanning 0.5 seconds and releases only this constraint. Active CAN stops temporarily use ACC solving in blended, retain stronger model braking and restore the selected mode on release.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Restart after changing. Independent of turn lamps, Share Data and Signal Assist. Only the exact 8-byte, metre-scale, vision-backed APP_trafficControl profile qualifies; six-byte DAS_road is rejected. Pedal input suppresses this feature until disengagement and new engagement. Other brands ignore the switch.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Verify raw vehicle CAN, direction relevance and the provisional 2 m stop buffer on a closed course before use. Late red can exceed braking capability. Signal loss after 0.5 seconds or target inconsistency requests takeover and soft-disable, which ultimately disengages; the driver must brake. No new Panda permission or road acceptance. Details: docs/user/en/tesla.md in the source repository.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaCanTrafficStop -->

<!-- CARROT:SETTING:END TeslaCanTrafficStop -->
