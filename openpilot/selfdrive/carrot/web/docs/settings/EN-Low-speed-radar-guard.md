<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="LowSpeedRadarGuard" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Low-speed radar guard

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN LowSpeedRadarGuard -->
<a id="LowSpeedRadarGuard"></a>

## Low-speed radar guard

`LowSpeedRadarGuard`

Up to 15 km/h, a confirmed closing radar lead can inhibit positive acceleration under openpilot longitudinal control. An occupied side or unavailable radar holds a new automatic turn request. A clear road and wall clearance cannot be determined from these signals.

<!-- CARROT:AUTO:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:AUTO:SOURCE facts="20f0cd195d38b70e1bebecdc380dd0450e2bd69b49ffe718a3990ee25e272164" semantic="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedRadarGuard -->

<!-- CARROT:MANUAL:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:REVIEW reviewed-for="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" reviewed-at="2026-11-27T22:32:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The front guard requires three separate radar samples of the same target within 7 m, closing faster than 0.5 m/s with at most two seconds to contact. It can remove positive acceleration. Stronger deceleration retains priority. A fresh complete Hyundai/Kia 0x180 or 0x235 corner scan is required to release the side veto when there is no positive detection. A wall or curb can lie outside sensor coverage.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LowSpeedRadarGuard -->

<!-- CARROT:SETTING:END LowSpeedRadarGuard -->
