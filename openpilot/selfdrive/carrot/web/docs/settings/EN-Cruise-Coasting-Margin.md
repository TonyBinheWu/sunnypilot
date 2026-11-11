<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_CARROT" param="CruiseCoastingPercent" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Coasting Margin

**Menu:** Driving \> Cruise & Gap \> Carrot Cruise

---

<!-- CARROT:SETTING:BEGIN CruiseCoastingPercent -->
<a id="CruiseCoastingPercent"></a>

## Cruise Coasting Margin

`CruiseCoastingPercent`

0% keeps existing control. Relaxes cruise braking above the set speed and restores it near the margin ceiling, without raising the set speed or disabling SCC. Applies only to ordinary cruise without leads, stopping, or external speed control.

<!-- CARROT:AUTO:BEGIN CruiseCoastingPercent -->
<!-- CARROT:AUTO:SOURCE facts="fff1bc9589632162b69ea7e5f987cfce217be4db14eb9026e021b97e18923fca" semantic="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `0%` ~ `10%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Driving \> Cruise & Gap \> Carrot Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseCoastingPercent -->

<!-- CARROT:MANUAL:BEGIN CruiseCoastingPercent -->
<!-- CARROT:REVIEW reviewed-for="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" reviewed-at="2026-09-25T08:35:39+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Relaxes only braking commands during ordinary cruise above the set speed. Increasing the value widens the overspeed band; decreasing it restores normal braking sooner.

- Relief increases over the first 10% of the band, and braking returns over its final 40%. Neither the set speed nor MPC target is raised, and SCC remains enabled.
- Requires a reference above 10km/h and the set speed, margin setting and eligibility unchanged for one second. The converted speed reference is fixed at entry; later conversion-ratio changes do not restart the wait or move the reference.
- Leads, cut-in candidates, stopping, curve limiting, external speed control, lane changes, and Experimental Mode prevent relief. A changed set speed or margin, or loss of eligibility, requires a new reference and another one-second wait.
- Does not apply during economy-control target increases or the existing CarrotCruise acceleration-limiting mode. Navigation caps at or below the coasting ceiling also prevent relief.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Changes are read approximately once per second while running. Select the disabled value to restore existing cruise braking.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

For a 100km/h set speed with a 5% margin, normal braking returns between 103 and 105km/h. This neither accelerates to 105km/h nor guarantees that actual speed stays below the ceiling.

A zero SCC acceleration request may still produce regeneration depending on the vehicle. Driving validation has not yet been completed.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseCoastingPercent -->

<!-- CARROT:SETTING:END CruiseCoastingPercent -->
