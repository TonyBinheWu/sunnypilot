<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="LateralTorqueKf" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKf\*0.001(100)

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKf -->
<a id="LateralTorqueKf"></a>

## \_LateralTorqueKf\*0.001(100)

`LateralTorqueKf`

Steering Feedforward Correction — 85 Recommended

<!-- CARROT:AUTO:BEGIN LateralTorqueKf -->
<!-- CARROT:AUTO:SOURCE facts="dfdc64375132ae1d5b99da2e46fca03b3bf92c247880c96e7620f7876e7ac736" semantic="ea6d27099c3e8610130f74384cd9fe8bee6c2a22a6291c942b50541fc25fcd81" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `0` ~ `200`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKf -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKf -->
<!-- CARROT:REVIEW reviewed-for="ea6d27099c3e8610130f74384cd9fe8bee6c2a22a6291c942b50541fc25fcd81" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the feedforward coefficient applied to predicted steering torque.

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
<!-- CARROT:MANUAL:END LateralTorqueKf -->

<!-- CARROT:SETTING:END LateralTorqueKf -->
