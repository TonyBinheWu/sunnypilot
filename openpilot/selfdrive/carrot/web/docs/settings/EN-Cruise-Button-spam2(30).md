<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_TEST" param="CruiseButtonTest2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Button spam2(30)

**Menu:** Driving \> Buttons & Presets \> Button Test

---

<!-- CARROT:SETTING:BEGIN CruiseButtonTest2 -->
<a id="CruiseButtonTest2"></a>

## Cruise Button spam2(30)

`CruiseButtonTest2`

For Non-Long Vehicle Only — Speed Button Signal Send Pause Time

<!-- CARROT:AUTO:BEGIN CruiseButtonTest2 -->
<!-- CARROT:AUTO:SOURCE facts="30900215ac5529b39c3edc8a7210668e7bb6da0330defa4a07fe79f7b7113946" semantic="d83180f0cb164cd36f0798b100d121a6667671fb0f64ae29c2fac426182f3c6f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `1` ~ `200`
- **Step:** `1`
- **Menu:** Driving \> Buttons & Presets \> Button Test
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonTest2 -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonTest2 -->
<!-- CARROT:REVIEW reviewed-for="d83180f0cb164cd36f0798b100d121a6667671fb0f64ae29c2fac426182f3c6f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

For Non-Long Vehicle Only — Speed Button Signal Send Pause Time.

- **Higher:** Increases the pause between button-message bursts.
- **Lower:** Decreases the pause.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Adjust this only on non-longitudinal vehicles that use stock SCC button messages, changing one item at a time and checking for missed or excessive inputs.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> This directly affects stock-SCC button messages on non-longitudinal vehicles. Record the default and adjust only on a verified vehicle.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonTest2 -->

<!-- CARROT:SETTING:END CruiseButtonTest2 -->
