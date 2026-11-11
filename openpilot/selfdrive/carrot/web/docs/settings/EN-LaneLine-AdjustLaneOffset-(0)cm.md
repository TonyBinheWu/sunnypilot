<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="AdjustLaneOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LaneLine: AdjustLaneOffset (0)cm

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN AdjustLaneOffset -->
<a id="AdjustLaneOffset"></a>

## LaneLine: AdjustLaneOffset (0)cm

`AdjustLaneOffset`

Corrects toward the road edge/inside of the curve

<!-- CARROT:AUTO:BEGIN AdjustLaneOffset -->
<!-- CARROT:AUTO:SOURCE facts="26ca36734c1dae896a72531a1912cb7b9910abe92658e597a835a08e93d81dfa" semantic="919b501dd31d3d3f258b212892e8fb3d2436b4872e6787e10d4fb65765fa6cfb" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0cm`
- **Range:** `0cm` ~ `500cm`
- **Step:** `10`
- **Display unit:** `cm`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AdjustLaneOffset -->

<!-- CARROT:MANUAL:BEGIN AdjustLaneOffset -->
<!-- CARROT:REVIEW reviewed-for="919b501dd31d3d3f258b212892e8fb3d2436b4872e6787e10d4fb65765fa6cfb" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Corrects toward the road edge/inside of the curve.

- **Higher:** Moves the correction in the positive direction.
- **Lower:** Moves it in the negative direction.
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
<!-- CARROT:MANUAL:END AdjustLaneOffset -->

<!-- CARROT:SETTING:END AdjustLaneOffset -->
