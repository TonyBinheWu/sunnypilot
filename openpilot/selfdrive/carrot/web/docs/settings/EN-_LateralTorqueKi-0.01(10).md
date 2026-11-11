<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="LateralTorqueKiV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKi\*0.01(10)

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKiV -->
<a id="LateralTorqueKiV"></a>

## \_LateralTorqueKi\*0.01(10)

`LateralTorqueKiV`

Steering Accumulated Error Correction — 20 Recommended

<!-- CARROT:AUTO:BEGIN LateralTorqueKiV -->
<!-- CARROT:AUTO:SOURCE facts="f599e6cb360c45afc60d1fb99441d8c0db3c17ac658580c3a31670406b1f4441" semantic="1009f0b89dab98fe24e61983fa04ccf3c2daebed428a26b892370ecf0301a095" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `10`
- **Range:** `0` ~ `200`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKiV -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKiV -->
<!-- CARROT:REVIEW reviewed-for="1009f0b89dab98fe24e61983fa04ccf3c2daebed428a26b892370ecf0301a095" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the integral term that corrects accumulated steering error.

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
<!-- CARROT:MANUAL:END LateralTorqueKiV -->

<!-- CARROT:SETTING:END LateralTorqueKiV -->
