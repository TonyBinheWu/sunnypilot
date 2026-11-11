<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_MODE" param="CruiseButtonMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Button Mode(0)

**Menu:** Driving \> Buttons & Presets \> Button Modes

---

<!-- CARROT:SETTING:BEGIN CruiseButtonMode -->
<a id="CruiseButtonMode"></a>

## Cruise Button Mode(0)

`CruiseButtonMode`

0:General, 1:User1, 2:User2, 3:User3(Use Speed Tables)

<!-- CARROT:AUTO:BEGIN CruiseButtonMode -->
<!-- CARROT:AUTO:SOURCE facts="205051a0b48c589da79c28675c5900307ec2d0eb122983e625874d1712676ff7" semantic="f106c313d9301e43d396835fadab742302d3dc37007a00554bf7f574204238c1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Driving \> Buttons & Presets \> Button Modes
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonMode -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonMode -->
<!-- CARROT:REVIEW reviewed-for="f106c313d9301e43d396835fadab742302d3dc37007a00554bf7f574204238c1" reviewed-at="2026-09-22T02:17:36+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — General
- `1` — User1
- `2` — User2
- `3` — User3(Use Speed Tables)

On Volkswagen, separate SET sets current cluster speed. RES restores saved pre-braking speed, otherwise retaining the existing set speed or using current speed if not initialized. This mode applies to separate +/-. Manual engagement remains tied to release of physical SET/RES.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Select the mode while parked, then verify short-press, long-press, and cancel behavior separately.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonMode -->

<!-- CARROT:SETTING:END CruiseButtonMode -->
