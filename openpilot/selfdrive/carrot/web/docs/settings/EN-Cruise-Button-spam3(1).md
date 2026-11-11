<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_TEST" param="CruiseButtonTest3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Button spam3(1)

**Menu:** Driving \> Buttons & Presets \> Button Test

---

<!-- CARROT:SETTING:BEGIN CruiseButtonTest3 -->
<a id="CruiseButtonTest3"></a>

## Cruise Button spam3(1)

`CruiseButtonTest3`

For Non-Long Vehicle Only — Consecutive Speed Button Signal Count

<!-- CARROT:AUTO:BEGIN CruiseButtonTest3 -->
<!-- CARROT:AUTO:SOURCE facts="67a1e3b9399234ed7f2b2cb87097f7bb592d07b20527ed275700e4f69488e335" semantic="af261696361d69a11ca78c75dec91ea37bd659d2db7fd9b1cb1ba1a8c17aa391" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `1` ~ `20`
- **Step:** `1`
- **Menu:** Driving \> Buttons & Presets \> Button Test
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonTest3 -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonTest3 -->
<!-- CARROT:REVIEW reviewed-for="af261696361d69a11ca78c75dec91ea37bd659d2db7fd9b1cb1ba1a8c17aa391" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

For Non-Long Vehicle Only — Consecutive Speed Button Signal Count.

- **Higher:** Increases the number of consecutive button messages.
- **Lower:** Decreases the consecutive count.
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
<!-- CARROT:MANUAL:END CruiseButtonTest3 -->

<!-- CARROT:SETTING:END CruiseButtonTest3 -->
