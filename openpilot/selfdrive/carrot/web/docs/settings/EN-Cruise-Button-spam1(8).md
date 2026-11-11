<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_TEST" param="CruiseButtonTest1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Button spam1(8)

**Menu:** Driving \> Buttons & Presets \> Button Test

---

<!-- CARROT:SETTING:BEGIN CruiseButtonTest1 -->
<a id="CruiseButtonTest1"></a>

## Cruise Button spam1(8)

`CruiseButtonTest1`

For Non-Long Vehicle Only, Speed Button Signal Send Restriction Time

<!-- CARROT:AUTO:BEGIN CruiseButtonTest1 -->
<!-- CARROT:AUTO:SOURCE facts="0c4c62c1e9ef06a4343db839f4f37d93fa38da68c6675b0658bdcbb5ea9c22e3" semantic="b76fc3c2fedf34451067daab249e5a3933c4cbbe94d61cbb0fd5198798b31a2f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `1` ~ `20`
- **Step:** `1`
- **Menu:** Driving \> Buttons & Presets \> Button Test
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonTest1 -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonTest1 -->
<!-- CARROT:REVIEW reviewed-for="b76fc3c2fedf34451067daab249e5a3933c4cbbe94d61cbb0fd5198798b31a2f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

For Non-Long Vehicle Only, Speed Button Signal Send Restriction Time.

- **Higher:** Lengthens each button-message sending period.
- **Lower:** Shortens the sending period.
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
<!-- CARROT:MANUAL:END CruiseButtonTest1 -->

<!-- CARROT:SETTING:END CruiseButtonTest1 -->
