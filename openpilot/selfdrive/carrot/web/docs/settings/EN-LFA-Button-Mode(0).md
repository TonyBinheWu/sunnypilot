<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_MODE" param="LfaButtonMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LFA Button Mode(0)

**Menu:** Driving \> Buttons & Presets \> Button Modes

---

<!-- CARROT:SETTING:BEGIN LfaButtonMode -->
<a id="LfaButtonMode"></a>

## LFA Button Mode(0)

`LfaButtonMode`

0:General, 1:Decel&Stop, leadCar ready, 2:CarrotCruise

<!-- CARROT:AUTO:BEGIN LfaButtonMode -->
<!-- CARROT:AUTO:SOURCE facts="f2b4837e8446407a66418112c70ee144577c67819002c4bdaeb9e58b85c42211" semantic="9c4b44838ae0dcff4397e38c706817d14778d81d616a5617a32fbc5b2d88e8ff" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Buttons & Presets \> Button Modes
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LfaButtonMode -->

<!-- CARROT:MANUAL:BEGIN LfaButtonMode -->
<!-- CARROT:REVIEW reviewed-for="9c4b44838ae0dcff4397e38c706817d14778d81d616a5617a32fbc5b2d88e8ff" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — General
- `1` — Decel&Stop, leadCar ready
- `2` — CarrotCruise
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Select the mode while parked, then verify short-press, long-press, and cancel behavior separately.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LfaButtonMode -->

<!-- CARROT:SETTING:END LfaButtonMode -->
