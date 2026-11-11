<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoTurnMapChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC Helper Map display(0)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoTurnMapChange -->
<a id="AutoTurnMapChange"></a>

## ATC Helper Map display(0)

`AutoTurnMapChange`

(APN) Turn On Map When ATC

<!-- CARROT:AUTO:BEGIN AutoTurnMapChange -->
<!-- CARROT:AUTO:SOURCE facts="c8c1c2154b81f626de00c00e1d294a8826d4821d676caa647bb33075a188b42c" semantic="e5a6acf262e3326cb0dab44709ee7c0a63122f628c93714fdb9143510beeead6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnMapChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnMapChange -->
<!-- CARROT:REVIEW reviewed-for="e5a6acf262e3326cb0dab44709ee7c0a63122f628c93714fdb9143510beeead6" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Switches the connected display to map mode when ATC turn control activates, then returns to the road view after the section.
- **Off:** ATC does not send display-switch commands.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Test where lane markings are clear and nearby traffic is absent, checking the wait, lane validation, and completion timing after signaling.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> This helper switches to the connected external navigation map while ATC is active.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoTurnMapChange -->

<!-- CARROT:SETTING:END AutoTurnMapChange -->
