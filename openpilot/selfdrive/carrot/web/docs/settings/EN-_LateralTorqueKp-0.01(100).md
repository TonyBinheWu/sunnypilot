<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="LateralTorqueKpV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueKp\*0.01(100)

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN LateralTorqueKpV -->
<a id="LateralTorqueKpV"></a>

## \_LateralTorqueKp\*0.01(100)

`LateralTorqueKpV`

Steering Response Speed (Instant Reaction) — 140 Recommended

<!-- CARROT:AUTO:BEGIN LateralTorqueKpV -->
<!-- CARROT:AUTO:SOURCE facts="0d81a1ea1b56529a4b31847b8497d7dc928d91ba28f7e210e4d4616c5cb5b989" semantic="03a3a5b716a1a1c2a0bb05b45da9e8adcadcf2e1c1a3232e2fbc606fc1ab928a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `0` ~ `200`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueKpV -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueKpV -->
<!-- CARROT:REVIEW reviewed-for="03a3a5b716a1a1c2a0bb05b45da9e8adcadcf2e1c1a3232e2fbc606fc1ab928a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the proportional term that responds immediately to steering error.

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
<!-- CARROT:MANUAL:END LateralTorqueKpV -->

<!-- CARROT:SETTING:END LateralTorqueKpV -->
