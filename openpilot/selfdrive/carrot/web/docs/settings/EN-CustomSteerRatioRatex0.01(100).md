<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="SteerRatioRate" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CustomSteerRatioRatex0.01(100)

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN SteerRatioRate -->
<a id="SteerRatioRate"></a>

## CustomSteerRatioRatex0.01(100)

`SteerRatioRate`

LiveSteerRatio Application Ratio (Requires CustomSR set to 0)

<!-- CARROT:AUTO:BEGIN SteerRatioRate -->
<!-- CARROT:AUTO:SOURCE facts="973cbb821a8c9f24e2121d154452c9014d351bfef15f1d658b1295b79a82f5f0" semantic="3dcdc5b26050ba384382fe8733f365d2de9ff1bc73e56b23703f73b6dce4381b" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100%`
- **Range:** `30%` ~ `200%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SteerRatioRate -->

<!-- CARROT:MANUAL:BEGIN SteerRatioRate -->
<!-- CARROT:REVIEW reviewed-for="3dcdc5b26050ba384382fe8733f365d2de9ff1bc73e56b23703f73b6dce4381b" reviewed-at="2026-09-30T12:27:06.503383+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

LiveSteerRatio Application Ratio (Requires CustomSR set to 0).

- **Higher:** Increases the multiplier applied to the learned steering ratio.
- **Lower:** Decreases that multiplier.

This also applies to VW MEB, including ID.4; selecting a valid manual steering ratio bypasses this multiplier. A saved rate outside the allowed range falls back to the unscaled learned ratio.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use small, one-at-a-time changes on the same straight and gentle curve, checking delay, oscillation, and recovery after driver input.

Previously ignored ID.4 values take effect after updating. Use `CustomSR=0` and `SteerRatioRate=100%` for the unchanged learned ratio.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> This multiplier applies to the learned steering ratio only when `CustomSR` is `0`.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SteerRatioRate -->

<!-- CARROT:SETTING:END SteerRatioRate -->
