<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowTpms" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show TPMS Info

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowTpms -->
<a id="ShowTpms"></a>

## Show TPMS Info

`ShowTpms`

0:None, 1: Upper, 2:Lower, 3: Both ※ Not applicable to C4 (MICI)

<!-- CARROT:AUTO:BEGIN ShowTpms -->
<!-- CARROT:AUTO:SOURCE facts="f8ed5c2efdf83fbcb38a1ee5bebeae57632b0357475be95e7e85f93180040c42" semantic="fd79f1bf1968efdfc0592e51e5336d2ab76734d8ffd69c233cc4444a22b4c036" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `1`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowTpms -->

<!-- CARROT:MANUAL:BEGIN ShowTpms -->
<!-- CARROT:REVIEW reviewed-for="8c41eb6b830837957be0bde4715e8c09993f67ca59b986365e08d8eab5ed8999" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — None
- `1` — Upper
- `2` — Lower
- `3` — Both
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check placement and readability on the driving display and enable only the information you need.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowTpms -->

<!-- CARROT:SETTING:END ShowTpms -->
