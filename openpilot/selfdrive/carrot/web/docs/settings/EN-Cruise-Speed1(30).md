<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_SPEEDTABLE" param="CruiseSpeed1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Speed1(30)

**Menu:** Driving \> Buttons & Presets \> Speed Presets

---

<!-- CARROT:SETTING:BEGIN CruiseSpeed1 -->
<a id="CruiseSpeed1"></a>

## Cruise Speed1(30)

`CruiseSpeed1`

Button Mode User 3, Stepwise Speed, 0: Road Speed Limit + Auto Speed Increase Offset

<!-- CARROT:AUTO:BEGIN CruiseSpeed1 -->
<!-- CARROT:AUTO:SOURCE facts="1ec99cb82823b49c24f695a9dae50073f8e512975de2f314c160cd955ceae143" semantic="7611e310ebea11fb8197231b9306cfd038c77d147da7f08f6315d1dfbaea2300" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `10km/h`
- **Range:** `0km/h` ~ `160km/h`
- **Step:** `10`
- **Display unit:** `km/h`
- **Menu:** Driving \> Buttons & Presets \> Speed Presets
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseSpeed1 -->

<!-- CARROT:MANUAL:BEGIN CruiseSpeed1 -->
<!-- CARROT:REVIEW reviewed-for="7611e310ebea11fb8197231b9306cfd038c77d147da7f08f6315d1dfbaea2300" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Button Mode User 3, Stepwise Speed.

- **Higher:** Raises the set speed for this step.
- **Lower:** Lowers the set speed for this step.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Set the button mode to User 3, then verify the step order and set speed at each step.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseSpeed1 -->

<!-- CARROT:SETTING:END CruiseSpeed1 -->
