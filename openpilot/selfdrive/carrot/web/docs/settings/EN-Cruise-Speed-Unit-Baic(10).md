<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_UNIT" param="CruiseSpeedUnitBasic" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Speed Unit Baic(10)

**Menu:** Driving \> Buttons & Presets \> Speed Units

---

<!-- CARROT:SETTING:BEGIN CruiseSpeedUnitBasic -->
<a id="CruiseSpeedUnitBasic"></a>

## Cruise Speed Unit Baic(10)

`CruiseSpeedUnitBasic`

SET/DECEL up/down speed unit(Basic unit)

<!-- CARROT:AUTO:BEGIN CruiseSpeedUnitBasic -->
<!-- CARROT:AUTO:SOURCE facts="75dec721e9ec758e5b5fe382040a2ff03c9ca8a24d67fd877d6ae774b067b03a" semantic="7b48bb82f966475975d3c3d2c777ca567eb1ed3846b4d9fa5f3ec085600de7a0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `10km/h`
- **Range:** `1km/h` ~ `100km/h`
- **Step:** `1`
- **Display unit:** `km/h`
- **Menu:** Driving \> Buttons & Presets \> Speed Units
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseSpeedUnitBasic -->

<!-- CARROT:MANUAL:BEGIN CruiseSpeedUnitBasic -->
<!-- CARROT:REVIEW reviewed-for="7b48bb82f966475975d3c3d2c777ca567eb1ed3846b4d9fa5f3ec085600de7a0" reviewed-at="2026-09-22T02:17:36+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

SET/DECEL up/down speed unit(Basic unit).

- **Higher:** Increases each set-speed step in the basic button mode.
- **Lower:** Reduces the basic adjustment step.

In Volkswagen normal mode, this increment applies to a short press of separate +/-. SET selects current speed and RES restores the previous set speed.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Verify the set-speed change amount and timing for both a single press and a long press.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseSpeedUnitBasic -->

<!-- CARROT:SETTING:END CruiseSpeedUnitBasic -->
