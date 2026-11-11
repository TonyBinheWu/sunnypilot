<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="LatMpcJerkCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.JerkCost(4)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN LatMpcJerkCost -->
<a id="LatMpcJerkCost"></a>

## \*LATMPC.JerkCost(4)

`LatMpcJerkCost`

(LaneMode) Lower values allow quicker steering — reduces smoothness

<!-- CARROT:AUTO:BEGIN LatMpcJerkCost -->
<!-- CARROT:AUTO:SOURCE facts="1fd7f8d85a39afd1f5d67392bb433f7c4cf2f1fd0eaf30d145af36d251ba00cc" semantic="b03aeed762639a7ad9e574bc0a93999bce2ccf72dd07f737014001472e26b1fb" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `1`
- **Range:** `0` ~ `200`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcJerkCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcJerkCost -->
<!-- CARROT:REVIEW reviewed-for="b03aeed762639a7ad9e574bc0a93999bce2ccf72dd07f737014001472e26b1fb" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(LaneMode) Lower values allow quicker steering — reduces smoothness.

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
<!-- CARROT:MANUAL:END LatMpcJerkCost -->

<!-- CARROT:SETTING:END LatMpcJerkCost -->
