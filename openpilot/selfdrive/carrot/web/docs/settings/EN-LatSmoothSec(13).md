<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="LatSmoothSec" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LatSmoothSec(13)

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN LatSmoothSec -->
<a id="LatSmoothSec"></a>

## LatSmoothSec(13)

`LatSmoothSec`

Lat smoothing values — Higher values smoother

<!-- CARROT:AUTO:BEGIN LatSmoothSec -->
<!-- CARROT:AUTO:SOURCE facts="e679e0b71375d0862ace1398270b92edc5b7f893c5415453ebded4f778d57e23" semantic="42a46c7c6b551635f61326eed6731f5eccaa1f0669f7bb23fa20a4f8626c95c2" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `13`
- **Range:** `1` ~ `30`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatSmoothSec -->

<!-- CARROT:MANUAL:BEGIN LatSmoothSec -->
<!-- CARROT:REVIEW reviewed-for="42a46c7c6b551635f61326eed6731f5eccaa1f0669f7bb23fa20a4f8626c95c2" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Lat smoothing values — Higher values smoother.

- **Higher:** Makes steering changes smoother and slower.
- **Lower:** Responds faster but can feel less smooth.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use small, one-at-a-time changes on the same straight and gentle curve, checking delay, oscillation, and recovery after driver input.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatSmoothSec -->

<!-- CARROT:SETTING:END LatSmoothSec -->
