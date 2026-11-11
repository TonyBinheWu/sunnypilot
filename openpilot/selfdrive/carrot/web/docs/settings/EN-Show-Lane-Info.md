<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowLaneInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Lane Info

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowLaneInfo -->
<a id="ShowLaneInfo"></a>

## Show Lane Info

`ShowLaneInfo`

-1:None, 0:Path, 1:Path+Lane, 2:Path+Lane+RoadEdge

<!-- CARROT:AUTO:BEGIN ShowLaneInfo -->
<!-- CARROT:AUTO:SOURCE facts="3963d0f2170aaa6243f0fe2f6377b4f5013607718e468c98cfc335fd57cc9efc" semantic="7c35ba7d1d497e19a704752026f79ad2d1e535149cf588d95bce85285926322b" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `1`
- **Range:** `-1` ~ `2`
- **Step:** `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowLaneInfo -->

<!-- CARROT:MANUAL:BEGIN ShowLaneInfo -->
<!-- CARROT:REVIEW reviewed-for="7c35ba7d1d497e19a704752026f79ad2d1e535149cf588d95bce85285926322b" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `-1` — None
- `0` — Path
- `1` — Path+Lane
- `2` — Path+Lane+RoadEdge
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check placement and readability on the driving display and enable only the information you need.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowLaneInfo -->

<!-- CARROT:SETTING:END ShowLaneInfo -->
