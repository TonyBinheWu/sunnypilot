<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_MODE" param="PaddleMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# PaddleShift Mode(0)

**Menu:** Driving \> Buttons & Presets \> Button Modes

---

<!-- CARROT:SETTING:BEGIN PaddleMode -->
<a id="PaddleMode"></a>

## PaddleShift Mode(0)

`PaddleMode`

After Regen paddle, 0:Cruise ON, 1:Cruise Ready, 2: decel & cruise ready, 3: CarrotCruise

<!-- CARROT:AUTO:BEGIN PaddleMode -->
<!-- CARROT:AUTO:SOURCE facts="7a9ce0415bab3acedb975bab8ce019fc113541533237561a3cff8b73595a4ae9" semantic="513264e6a1d57186ce13925ba169f9b25c61b0d5d02385d078e00fd84cb40d9d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `1`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Driving \> Buttons & Presets \> Button Modes
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END PaddleMode -->

<!-- CARROT:MANUAL:BEGIN PaddleMode -->
<!-- CARROT:REVIEW reviewed-for="513264e6a1d57186ce13925ba169f9b25c61b0d5d02385d078e00fd84cb40d9d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Cruise ON
- `1` — Cruise Ready
- `2` — decel & cruise ready
- `3` — CarrotCruise
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Select the mode while parked, then verify short-press, long-press, and cancel behavior separately.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END PaddleMode -->

<!-- CARROT:SETTING:END PaddleMode -->
