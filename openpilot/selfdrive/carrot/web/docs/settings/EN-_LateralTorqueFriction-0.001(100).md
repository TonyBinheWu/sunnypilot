<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="LateralTorqueFriction" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueFriction\*0.001(100)

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN LateralTorqueFriction -->
<a id="LateralTorqueFriction"></a>

## \_LateralTorqueFriction\*0.001(100)

`LateralTorqueFriction`

More fine steering at higher values — 0-50 recommended

<!-- CARROT:AUTO:BEGIN LateralTorqueFriction -->
<!-- CARROT:AUTO:SOURCE facts="a1d6942df0538ffe1f2297c7bb04493e34ba10670eae20bc3bbdfb56bd6f79c5" semantic="bcb493a10728312a73f302531a0693387e121c32f1573d25390eaa2d30c5454a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `0` ~ `1000`
- **Step:** `10`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueFriction -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueFriction -->
<!-- CARROT:REVIEW reviewed-for="bcb493a10728312a73f302531a0693387e121c32f1573d25390eaa2d30c5454a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the steering-system friction compensation coefficient.

- **Higher:** Increases friction compensation and fine steering torque.
- **Lower:** Reduces friction compensation and fine steering torque.
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
<!-- CARROT:MANUAL:END LateralTorqueFriction -->

<!-- CARROT:SETTING:END LateralTorqueFriction -->
