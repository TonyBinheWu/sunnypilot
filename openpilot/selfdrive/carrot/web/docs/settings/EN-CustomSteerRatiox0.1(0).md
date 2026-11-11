<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="CustomSR" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CustomSteerRatiox0.1(0)

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN CustomSR -->
<a id="CustomSR"></a>

## CustomSteerRatiox0.1(0)

`CustomSR`

Steering Ratio (Refer to Vehicle Specs), 0: Uses LiveSteerRatio

<!-- CARROT:AUTO:BEGIN CustomSR -->
<!-- CARROT:AUTO:SOURCE facts="018567132cbaa8763f00f7dfaa3d150551aed52924712e6788e30a2d1a7c5e45" semantic="ac448bdc0d0511e23b7beef678bc36d35b02b4610877afe79699ea4a590e9210" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `300`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSR -->

<!-- CARROT:MANUAL:BEGIN CustomSR -->
<!-- CARROT:REVIEW reviewed-for="ac448bdc0d0511e23b7beef678bc36d35b02b4610877afe79699ea4a590e9210" reviewed-at="2026-09-30T12:27:06.503886+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Steering Ratio (Refer to Vehicle Specs).

- **Higher:** Uses a larger fixed steering ratio, changing the steering angle calculated for the same curvature.
- **Lower:** Uses a smaller fixed steering ratio.

This also applies to VW MEB, including ID.4, and changes are reread by the control loop. A stored value times 0.1 above 1.0 selects the manual ratio; otherwise the learned ratio and `SteerRatioRate` apply. Selecting a manual ratio does not stop SR learning.
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
> `0` uses the learned steering ratio. A direct custom value takes precedence over the `SteerRatioRate` multiplier.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSR -->

<!-- CARROT:SETTING:END CustomSR -->
