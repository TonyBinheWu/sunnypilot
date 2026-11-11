<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoTurnControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: AutoTurnControl

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControl -->
<a id="AutoTurnControl"></a>

## ATC: AutoTurnControl

`AutoTurnControl`

0: off, 1: lane change/turn, 2: lane change/turn + speed, 3: speed. Set the right lane-change distance in details. Zero metres disables it. The add-on operates with mode 1 or 2.

<!-- CARROT:AUTO:BEGIN AutoTurnControl -->
<!-- CARROT:AUTO:SOURCE facts="64653571dbab02bb4fa4e0a769088d32ba07e3b3e10ab903da2d6a077c0eb171" semantic="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControl -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControl -->
<!-- CARROT:REVIEW reviewed-for="e075079f91a03599fc073d2fd981a0d2f880dba4f6b9252ca9cc7782a5ecb64d" reviewed-at="2026-11-02T22:15:29.511960+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Mode 0 disables ATC, 1 controls lane changes and turns, 2 also controls speed, and 3 controls speed only. The right-turn distance add-on requests a right indicator within its selected distance in modes 1 and 2.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Select the right lane-change distance in ATC details. Higher values check conditions earlier, while lower values wait until closer to the turn.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

On restart, retired mode 4 migrates to mode 1. The distance becomes 250m when no separate value exists, and an explicit value is preserved.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END AutoTurnControl -->

<!-- CARROT:SETTING:END AutoTurnControl -->
