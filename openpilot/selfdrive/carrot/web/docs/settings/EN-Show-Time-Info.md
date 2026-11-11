<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowDateTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Time Info

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowDateTime -->
<a id="ShowDateTime"></a>

## Show Time Info

`ShowDateTime`

0:None, 1:Time/Date, 2:Time, 3:Date

<!-- CARROT:AUTO:BEGIN ShowDateTime -->
<!-- CARROT:AUTO:SOURCE facts="c0339d655dc3ec6f64eb9fd1a4a5a3cc6e0371253c293da7ebe5089e74a4f765" semantic="8a8a68471ac48ff4050425e0bbfaa30b75d9672c261cc13c269e729cc3d39c41" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `1`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowDateTime -->

<!-- CARROT:MANUAL:BEGIN ShowDateTime -->
<!-- CARROT:REVIEW reviewed-for="8a8a68471ac48ff4050425e0bbfaa30b75d9672c261cc13c269e729cc3d39c41" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — None
- `1` — Time/Date
- `2` — Time
- `3` — Date
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check placement and readability on the driving display and enable only the information you need.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowDateTime -->

<!-- CARROT:SETTING:END ShowDateTime -->
