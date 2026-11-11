<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowDebugUI" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Debug Info

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowDebugUI -->
<a id="ShowDebugUI"></a>

## Show Debug Info

`ShowDebugUI`

Show Debug Info

<!-- CARROT:AUTO:BEGIN ShowDebugUI -->
<!-- CARROT:AUTO:SOURCE facts="91da89bf0eefc2a49b8555778b2850db177779df505e126bb8f918a30c36ffd5" semantic="5427f7c6ad263c8644a81441bc61043f741eccdf5c7938a34fb92f7a0320090d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `1`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowDebugUI -->

<!-- CARROT:MANUAL:BEGIN ShowDebugUI -->
<!-- CARROT:REVIEW reviewed-for="5427f7c6ad263c8644a81441bc61043f741eccdf5c7938a34fb92f7a0320090d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Hides debug information.
- `1`, `2` — In the current implementation, both show debug information on the driving display.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check placement and readability on the driving display and enable only the information you need.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowDebugUI -->

<!-- CARROT:SETTING:END ShowDebugUI -->
