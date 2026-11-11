<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="CenterToFrontRatio" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Center of gravity ratio

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN CenterToFrontRatio -->
<a id="CenterToFrontRatio"></a>

## Center of gravity ratio

`CenterToFrontRatio`

0=vehicle default. Otherwise 31–69%=wheelbase×ratio. Changes apply smoothly without restarting. Defaults: Hyundai/Kia/Genesis 40%, Toyota/Lexus 44%, Mazda 41%, Volkswagen 45%; Honda varies by model. Compare a small increase for late entry or a decrease for cutting inside. Effects depend on lane mode and vehicle. Keep SAD and SR unchanged. Revert to the previous value or 0 if worse.

<!-- CARROT:AUTO:BEGIN CenterToFrontRatio -->
<!-- CARROT:AUTO:SOURCE facts="0c8945826d8c4764c3d876bbb2cce1a21f8517cc8cbe65a66cd742c661b3afd4" semantic="ffcefcd7552894afdf0dbf200567b02117bac3fdd8a60a8f29a28907d3976f52" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `0%` ~ `69%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CenterToFrontRatio -->

<!-- CARROT:MANUAL:BEGIN CenterToFrontRatio -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CenterToFrontRatio -->

<!-- CARROT:SETTING:END CenterToFrontRatio -->
