<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="LateralTorqueAccelFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueAccelFactor\*0.001(2500)

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN LateralTorqueAccelFactor -->
<a id="LateralTorqueAccelFactor"></a>

## \_LateralTorqueAccelFactor\*0.001(2500)

`LateralTorqueAccelFactor`

As the value decreases, the torque becomes stronger up to a point, then weakens — Uses the value at the strongest point.

<!-- CARROT:AUTO:BEGIN LateralTorqueAccelFactor -->
<!-- CARROT:AUTO:SOURCE facts="f9748716e58b422239b1164f5cbb5f8c9c1abdc6b74690d3e4f36c5042e1fb59" semantic="746c0daa75a2f8c2391948cd47d2956c33436ee89b75ae1080fe4a6a40d6d552" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `2500`
- **Range:** `1000` ~ `6000`
- **Step:** `100`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueAccelFactor -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueAccelFactor -->
<!-- CARROT:REVIEW reviewed-for="746c0daa75a2f8c2391948cd47d2956c33436ee89b75ae1080fe4a6a40d6d552" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the factor that converts requested lateral acceleration into steering torque.

This coefficient is non-linear: reducing it strengthens torque up to a point, after which torque weakens again. Find the strongest usable point in small steps on the actual vehicle.
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
<!-- CARROT:MANUAL:END LateralTorqueAccelFactor -->

<!-- CARROT:SETTING:END LateralTorqueAccelFactor -->
