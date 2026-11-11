<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="LateralTorqueKd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKd\*0.01(0)

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKd -->
<a id="LateralTorqueKd"></a>

## \_LateralTorqueKd\*0.01(0)

`LateralTorqueKd`

Steering Derivative Gain, 0 Recommended

<!-- CARROT:AUTO:BEGIN LateralTorqueKd -->
<!-- CARROT:AUTO:SOURCE facts="b64141994e286697239c5c8125635ca3d49c80602b06368c0064b0fee57e98e8" semantic="f4b07835f8d82647a8e9661e9116ca1f5478c8d37cdf844014eb000c7d90ea9a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `10000`
- **Step:** `10`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKd -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKd -->
<!-- CARROT:REVIEW reviewed-for="f4b07835f8d82647a8e9661e9116ca1f5478c8d37cdf844014eb000c7d90ea9a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the derivative term that responds to rapid steering-error changes.

- **Higher:** Increases the contribution of this torque-control term.
- **Lower:** Reduces that contribution.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On torque-control vehicles, change one coefficient in small steps and compare torque during straight-line return, gentle curves, and driver override.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LateralTorqueKd -->

<!-- CARROT:SETTING:END LateralTorqueKd -->
