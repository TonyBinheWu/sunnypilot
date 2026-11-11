<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_LONGTUNE" param="LongTuningKiV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Long KiV(0)x0.001

**Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning

---

<!-- CARROT:SETTING:BEGIN LongTuningKiV -->
<a id="LongTuningKiV"></a>

## Long KiV(0)x0.001

`LongTuningKiV`

Longitudinal integral gain for accumulated error correction. Standard Hyundai, Kia, and Genesis longitudinal control is fixed at Ki 0, so this setting is hidden and ignored on those vehicles. Toyota/Lexus fix the common Ki=0 to avoid duplicate correction before their dedicated controller; this setting is hidden and saved values are ignored. An identified Ray EV Comma Pedal configuration exposes this setting and applies the saved value to speed PID within approximately one second. Actual Ki is the stored value multiplied by 0.001.

<!-- CARROT:AUTO:BEGIN LongTuningKiV -->
<!-- CARROT:AUTO:SOURCE facts="afa4f04878a1aa65031d580537a083fd34bfdd1294fc64cefadf7e5611af1cb7" semantic="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `2000`
- **Step:** `1`
- **Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKiV -->

<!-- CARROT:MANUAL:BEGIN LongTuningKiV -->
<!-- CARROT:REVIEW reviewed-for="408a16f2cac3b273bfca7a6a8fe50a70b9f2aed1b3ad6042d70f49451eb04700" reviewed-at="2026-11-11T05:33:10.270695+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the longitudinal integral term that corrects accumulated speed error.

- **Higher:** Increases the contribution of this longitudinal-control term.
- **Lower:** Reduces that contribution.

Volkswagen MEB vehicles, including ID.4, have single-point Kp and Ki tunes, so saved Kp/Ki/Kf settings apply. Updating does not reset previously saved values.
On Ray EV with a detected Comma Pedal and active openpilot longitudinal control, Long Kp/Ki/Kf are visible and their saved values apply to the speed PID. Values load at startup and refresh about once per second during operation.

Other Hyundai/Kia/Genesis configurations fix common Kp/Ki/Kf at 1/0/1. Toyota/Lexus fix them at 0/0/1 because their dedicated vehicle controller corrects acceleration tracking.
The actual Ki coefficient is the saved value × 0.001. A saved value of 50 applies 0.050, and 100 applies 0.100.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use small, one-at-a-time changes for the same target-speed transition and compare overshoot, oscillation, and response delay.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LongTuningKiV -->

<!-- CARROT:SETTING:END LongTuningKiV -->
