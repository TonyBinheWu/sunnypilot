<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="LatMpcMotionCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.MotionCost(7)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN LatMpcMotionCost -->
<a id="LatMpcMotionCost"></a>

## \*LATMPC.MotionCost(7)

`LatMpcMotionCost`

(LaneMode) Heading Weight

<!-- CARROT:AUTO:BEGIN LatMpcMotionCost -->
<!-- CARROT:AUTO:SOURCE facts="818aa45e59d1a028d0770ec52be212c65866660167ee7e8bfcc1a22f5f307498" semantic="1bdf8d77309360a95334d5df9779a59844b5330500ee823a8f43986ad8d5667f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `7`
- **Range:** `0` ~ `500`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcMotionCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcMotionCost -->
<!-- CARROT:REVIEW reviewed-for="1bdf8d77309360a95334d5df9779a59844b5330500ee823a8f43986ad8d5667f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(LaneMode) Heading Weight.

- **Higher:** Increases the MPC cost and suppression weight for this item.
- **Lower:** Allows that motion more readily.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Repeat the same lane and curve while adjusting one item at a time, comparing path tracking, steering response, and smoothness together.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatMpcMotionCost -->

<!-- CARROT:SETTING:END LatMpcMotionCost -->
