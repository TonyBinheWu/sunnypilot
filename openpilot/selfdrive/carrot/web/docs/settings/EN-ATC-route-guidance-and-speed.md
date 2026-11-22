<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC route guidance and speed

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC route guidance and speed

`AutoTurnControl`

0 off, 1 route cues, 2 route cues and speed control, 3 speed control. Navigation shows exits and turns. The driver selects the direction for a lane change.

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="048e98d51b90d1784c61f57ca50c31276ed49a97cd4749714f6a31058b0e66bc" semantic="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="c60e74ae9f02f3b4ca847ca4e7f0b5d7a9e4b85043058d06861a116e22426191" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

0 off, 1 route cues, 2 route cues and speed control, 3 speed control. Navigation shows exits and turns. The driver selects the direction for a lane change.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Choose mode 1 for junction cues, mode 2 to include turn-speed control, or mode 3 for speed control alone.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

To change lanes, first check the adjacent lane and signal your intended direction.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
