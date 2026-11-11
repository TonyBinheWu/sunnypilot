<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="LatMpcAccelCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.AccelCost(120)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN LatMpcAccelCost -->
<a id="LatMpcAccelCost"></a>

## \*LATMPC.AccelCost(120)

`LatMpcAccelCost`

(LaneMode) Lateral Acceleration Limit — Lower values increase agility but reduce stability

<!-- CARROT:AUTO:BEGIN LatMpcAccelCost -->
<!-- CARROT:AUTO:SOURCE facts="b7589c56637d57516cf55cb574670e248af3b0afcdf7260bdc432b2559bf4b93" semantic="8538f6cbd23edf0ba7f4d95ad4afb9b20e5a66792ca42c8559874d43490b0ca6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `0` ~ `500`
- **Step:** `10`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcAccelCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcAccelCost -->
<!-- CARROT:REVIEW reviewed-for="8538f6cbd23edf0ba7f4d95ad4afb9b20e5a66792ca42c8559874d43490b0ca6" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(LaneMode) Lateral Acceleration Limit — Lower values increase agility but reduce stability.

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
<!-- CARROT:MANUAL:END LatMpcAccelCost -->

<!-- CARROT:SETTING:END LatMpcAccelCost -->
