<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="LateralTorqueCustom" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_LateralTorqueCustom(0)

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN LateralTorqueCustom -->
<a id="LateralTorqueCustom"></a>

## \_LateralTorqueCustom(0)

`LateralTorqueCustom`

Use Custom Torque(TorqueAccelFactor, FrictionFactor)

<!-- CARROT:AUTO:BEGIN LateralTorqueCustom -->
<!-- CARROT:AUTO:SOURCE facts="5b10ab71a039a23a17d8d86842841795a63874cebc963b80a49552eca8335384" semantic="931515b55fa1df2997b5da0e909ee948b8e957adb02298be36935346c8429d94" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `1`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LateralTorqueCustom -->

<!-- CARROT:MANUAL:BEGIN LateralTorqueCustom -->
<!-- CARROT:REVIEW reviewed-for="931515b55fa1df2997b5da0e909ee948b8e957adb02298be36935346c8429d94" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Uses the user acceleration, friction, and PID coefficients for torque control.
- **Off:** Uses the default torque coefficients supplied by the vehicle interface and live learning.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On torque-control vehicles, change one coefficient in small steps and compare torque during straight-line return, gentle curves, and driver override.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> Custom torque coefficients apply only to torque-control vehicles. Enable this setting to use the custom acceleration and friction coefficients.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LateralTorqueCustom -->

<!-- CARROT:SETTING:END LateralTorqueCustom -->
