<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_PATH" param="ShowPathColorLane" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Path Color:LaneMode(3)

**Menu:** Display \> Path Display

---

<!-- CARROT:SETTING:BEGIN ShowPathColorLane -->
<a id="ShowPathColorLane"></a>

## Show Path Color:LaneMode(3)

`ShowPathColorLane`

(+10:stroke)0(R),1(O),2(Y),3(B),5(N),6(V),7(K),8(W),9(B),20:Auto

<!-- CARROT:AUTO:BEGIN ShowPathColorLane -->
<!-- CARROT:AUTO:SOURCE facts="5402b311281cc69f127d161b55cbae802d59ae613fe88fabfd85e9febca6f735" semantic="d7455a9fd2a86afc0293993b98b72bc99a8a9c2a0375adef24f7a5d5888c9f38" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `3`
- **Range:** `0` ~ `20`
- **Step:** `1`
- **Menu:** Display \> Path Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColorLane -->

<!-- CARROT:MANUAL:BEGIN ShowPathColorLane -->
<!-- CARROT:REVIEW reviewed-for="d7455a9fd2a86afc0293993b98b72bc99a8a9c2a0375adef24f7a5d5888c9f38" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

`0`–`9` select red, orange, yellow, green, blue, navy, violet, brown, white, and black for the lane-mode path. `10`–`19` add an emphasis outline, and `20` selects color automatically from driving state.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Switch cruise and lane-mode states on the driving display and verify that path shape and color change as intended.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColorLane -->

<!-- CARROT:SETTING:END ShowPathColorLane -->
