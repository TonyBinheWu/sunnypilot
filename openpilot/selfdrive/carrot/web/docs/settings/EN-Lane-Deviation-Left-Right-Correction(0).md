<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_CENTER" param="PathOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Lane Deviation Left/Right Correction(0)

**Menu:** Driving \> Steering \> Centering

---

<!-- CARROT:SETTING:BEGIN PathOffset -->
<a id="PathOffset"></a>

## Lane Deviation Left/Right Correction(0)

`PathOffset`

LaneMode only — (-)Left / (+)Right

<!-- CARROT:AUTO:BEGIN PathOffset -->
<!-- CARROT:AUTO:SOURCE facts="16243acd6c26080f63be4388c47a94547fdb2d7f734a7f34015a3e88271068f1" semantic="81aef93bf00308504aceb19384c7229c79421ee80c58f4397de30e222059d1d7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0cm`
- **Range:** `-150cm` ~ `150cm`
- **Step:** `1`
- **Display unit:** `cm`
- **Menu:** Driving \> Steering \> Centering
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END PathOffset -->

<!-- CARROT:MANUAL:BEGIN PathOffset -->
<!-- CARROT:REVIEW reviewed-for="81aef93bf00308504aceb19384c7229c79421ee80c58f4397de30e222059d1d7" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

LaneMode only — (-)Left / (+)Right.

- **Negative:** Moves the target path left.
- **Positive:** Moves the target path right.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Evaluate on a flat, straight road at a steady speed, changing one step at a time and comparing whether left/right bias is reduced.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END PathOffset -->

<!-- CARROT:SETTING:END PathOffset -->
