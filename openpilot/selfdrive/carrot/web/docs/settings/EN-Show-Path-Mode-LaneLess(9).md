<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_PATH" param="ShowPathMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Path Mode:LaneLess(9)

**Menu:** Display \> Path Display

---

<!-- CARROT:SETTING:BEGIN ShowPathMode -->
<a id="ShowPathMode"></a>

## Show Path Mode:LaneLess(9)

`ShowPathMode`

0:stock,1,2:REC,3,4:^^,5,6:REC,7,8:^^,9,10,11:smooth^^,12:smooth2^^,13:3lines,14:2lines,15:1lines

<!-- CARROT:AUTO:BEGIN ShowPathMode -->
<!-- CARROT:AUTO:SOURCE facts="73d56f537a4a516fa0aeb26e84150c64da678014509b107242c3890eac3febeb" semantic="d31a5fd649594fe0f0ac8dc0f4999b3002731d1ad199cfccd1b0230368c0bd76" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `9`
- **Range:** `0` ~ `15`
- **Step:** `1`
- **Menu:** Display \> Path Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathMode -->

<!-- CARROT:MANUAL:BEGIN ShowPathMode -->
<!-- CARROT:REVIEW reviewed-for="d31a5fd649594fe0f0ac8dc0f4999b3002731d1ad199cfccd1b0230368c0bd76" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Uses the stock path shape.
- `1`–`8` — Uses rectangle and chevron-style animated paths.
- `9`–`12` — Uses smooth chevron-style paths.
- `13`, `14`, `15` — Uses three-line, two-line, and one-line paths respectively.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Switch cruise and lane-mode states on the driving display and verify that path shape and color change as intended.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathMode -->

<!-- CARROT:SETTING:END ShowPathMode -->
