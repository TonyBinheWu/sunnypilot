<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="LatMpcSteeringRateCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.SteerRateCost(7)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN LatMpcSteeringRateCost -->
<a id="LatMpcSteeringRateCost"></a>

## \*LATMPC.SteerRateCost(7)

`LatMpcSteeringRateCost`

(LaneMode) Steering Rate Limit — Lower values make steering more aggressive

<!-- CARROT:AUTO:BEGIN LatMpcSteeringRateCost -->
<!-- CARROT:AUTO:SOURCE facts="63d86f29132607ca3c976ff87b439cd5b3fe2b95eb3a06a68afe5da62013af87" semantic="abb62754276e8852ac2b76df32326edddc868ac4e65e04789efd359aa48f1f74" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `7`
- **Range:** `0` ~ `1000`
- **Step:** `100`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcSteeringRateCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcSteeringRateCost -->
<!-- CARROT:REVIEW reviewed-for="abb62754276e8852ac2b76df32326edddc868ac4e65e04789efd359aa48f1f74" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(LaneMode) Steering Rate Limit — Lower values make steering more aggressive.

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
<!-- CARROT:MANUAL:END LatMpcSteeringRateCost -->

<!-- CARROT:SETTING:END LatMpcSteeringRateCost -->
