<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="LatMpcPathCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.PathCost(200)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN LatMpcPathCost -->
<a id="LatMpcPathCost"></a>

## \*LATMPC.PathCost(200)

`LatMpcPathCost`

(LaneMode) Path Following Weight — Higher values prioritize the path

<!-- CARROT:AUTO:BEGIN LatMpcPathCost -->
<!-- CARROT:AUTO:SOURCE facts="23d4e2c427392b4328573eaad0a36a44f76e911fec46b049953006812dea3abb" semantic="b83cc299182908b4d8c01ed9a897df4983bc1c8e59c535005d5f9ddde372c233" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `200`
- **Range:** `0` ~ `500`
- **Step:** `10`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcPathCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcPathCost -->
<!-- CARROT:REVIEW reviewed-for="b83cc299182908b4d8c01ed9a897df4983bc1c8e59c535005d5f9ddde372c233" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(LaneMode) Path Following Weight — Higher values prioritize the path.

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
<!-- CARROT:MANUAL:END LatMpcPathCost -->

<!-- CARROT:SETTING:END LatMpcPathCost -->
