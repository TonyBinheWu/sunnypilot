<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_PATH" param="CarrotTireTrajectory" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tire Trajectory

**Menu:** Display \> Path Display

---

<!-- CARROT:SETTING:BEGIN CarrotTireTrajectory -->
<a id="CarrotTireTrajectory"></a>

## Tire Trajectory

`CarrotTireTrajectory`

Display tire paths with a lane-departure gradient (green-\>red) over the predicted path, plus an L/R/C offset indicator. 0:Off, 1:On

<!-- CARROT:AUTO:BEGIN CarrotTireTrajectory -->
<!-- CARROT:AUTO:SOURCE facts="8116e41de3f91246d98a09dc84cec5abecb2e9908fa1019e352080492cab3500" semantic="5a96ee68d440c85103f4c4ff1d0ac55cc74ac347d5e3536e424bbf25810c2a34" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Display \> Path Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotTireTrajectory -->

<!-- CARROT:MANUAL:BEGIN CarrotTireTrajectory -->
<!-- CARROT:REVIEW reviewed-for="5a96ee68d440c85103f4c4ff1d0ac55cc74ac347d5e3536e424bbf25810c2a34" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Off
- `1` — On
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Switch cruise and lane-mode states on the driving display and verify that path shape and color change as intended.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CarrotTireTrajectory -->

<!-- CARROT:SETTING:END CarrotTireTrajectory -->
