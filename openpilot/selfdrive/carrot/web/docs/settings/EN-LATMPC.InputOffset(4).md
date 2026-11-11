<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="LatMpcInputOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \*LATMPC.InputOffset(4)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN LatMpcInputOffset -->
<a id="LatMpcInputOffset"></a>

## \*LATMPC.InputOffset(4)

`LatMpcInputOffset`

(LaneMode) MPC Input Compensation — Higher values enter curves earlier

<!-- CARROT:AUTO:BEGIN LatMpcInputOffset -->
<!-- CARROT:AUTO:SOURCE facts="f4da4b08afddceba309abe73b42c7df2bb22559541641758e39a4fafc86470e8" semantic="efc63caea6708ae570390d3c639d780d27edaa7d333175c03cd31e82d16b81cf" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `4`
- **Range:** `0` ~ `20`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcInputOffset -->

<!-- CARROT:MANUAL:BEGIN LatMpcInputOffset -->
<!-- CARROT:REVIEW reviewed-for="efc63caea6708ae570390d3c639d780d27edaa7d333175c03cd31e82d16b81cf" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(LaneMode) MPC Input Compensation — Higher values enter curves earlier.

- **Higher:** Advances MPC input and responds to curves earlier.
- **Lower:** Delays curve response.
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
<!-- CARROT:MANUAL:END LatMpcInputOffset -->

<!-- CARROT:SETTING:END LatMpcInputOffset -->
