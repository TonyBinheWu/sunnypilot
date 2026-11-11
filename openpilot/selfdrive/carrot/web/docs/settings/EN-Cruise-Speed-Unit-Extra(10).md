<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_UNIT" param="CruiseSpeedUnit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Speed Unit Extra(10)

**Menu:** Driving \> Buttons & Presets \> Speed Units

---

<!-- CARROT:SETTING:BEGIN CruiseSpeedUnit -->
<a id="CruiseSpeedUnit"></a>

## Cruise Speed Unit Extra(10)

`CruiseSpeedUnit`

SET/DECEL up/down speed unit(mode1,2,3, GasTok)

<!-- CARROT:AUTO:BEGIN CruiseSpeedUnit -->
<!-- CARROT:AUTO:SOURCE facts="0d9f215f78c75732f52e835b5be42cf6868a82887edef00786f8fb7fd5d78677" semantic="a5e07bb426bb832d07d78bd6f304a09aae259509b726f72c8de9fb610763a878" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `10km/h`
- **Range:** `1km/h` ~ `100km/h`
- **Step:** `1`
- **Display unit:** `km/h`
- **Menu:** Driving \> Buttons & Presets \> Speed Units
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseSpeedUnit -->

<!-- CARROT:MANUAL:BEGIN CruiseSpeedUnit -->
<!-- CARROT:REVIEW reviewed-for="a5e07bb426bb832d07d78bd6f304a09aae259509b726f72c8de9fb610763a878" reviewed-at="2026-09-22T02:17:36+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

SET/DECEL up/down speed unit(mode1,2,3, GasTok).

- **Higher:** Increases each set-speed step in user button modes and accelerator-tap operation.
- **Lower:** Reduces each adjustment step.

On Volkswagen, this unit applies to separate +/- speed adjustments, not to SET selecting current speed or RES restoring the previous speed. The 10 km/h step for long presses and stage-two swipes is unchanged by this setting.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Verify the set-speed change amount and timing for both a single press and a long press.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseSpeedUnit -->

<!-- CARROT:SETTING:END CruiseSpeedUnit -->
