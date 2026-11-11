<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_PATH" param="ShowPathModeLane" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Path Mode:LaneMode(11)

**Menu:** Display \> Path Display

---

<!-- CARROT:SETTING:BEGIN ShowPathModeLane -->
<a id="ShowPathModeLane"></a>

## Show Path Mode:LaneMode(11)

`ShowPathModeLane`

0:stock,1,2:REC,3,4:^^,5,6:REC,7,8:^^,9,10,11:smooth^^,12:smooth2^^,13:3lines,14:2lines,15:1lines

<!-- CARROT:AUTO:BEGIN ShowPathModeLane -->
<!-- CARROT:AUTO:SOURCE facts="615b0a3255dd56230238c439a6de7797738a3a9a7f32b85bdd082bc03dd5fa64" semantic="84dcae423af30a9d71a99b3233ad4685a33a27d494e4c726b488130eb594905c" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `11`
- **Range:** `0` ~ `15`
- **Step:** `1`
- **Menu:** Display \> Path Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathModeLane -->

<!-- CARROT:MANUAL:BEGIN ShowPathModeLane -->
<!-- CARROT:REVIEW reviewed-for="84dcae423af30a9d71a99b3233ad4685a33a27d494e4c726b488130eb594905c" reviewed-at="2026-07-24T16:44:29+09:00" -->
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
<!-- CARROT:MANUAL:END ShowPathModeLane -->

<!-- CARROT:SETTING:END ShowPathModeLane -->
