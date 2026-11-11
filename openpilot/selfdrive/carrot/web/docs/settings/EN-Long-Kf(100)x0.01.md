<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_LONGTUNE" param="LongTuningKf" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Long Kf(100)x0.01

**Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning

---

<!-- CARROT:SETTING:BEGIN LongTuningKf -->
<a id="LongTuningKf"></a>

## Long Kf(100)x0.01

`LongTuningKf`

Feeds target acceleration forward in both acceleration and braking directions. Standard Hyundai, Kia, and Genesis longitudinal control is fixed at Kf 1.0, so this setting is hidden and ignored on those vehicles. Toyota/Lexus fix the common Kf=1 to avoid duplicate correction before their dedicated controller; this setting is hidden and saved values are ignored. An identified Ray EV Comma Pedal configuration exposes this setting and applies the saved value to speed PID within approximately one second.

<!-- CARROT:AUTO:BEGIN LongTuningKf -->
<!-- CARROT:AUTO:SOURCE facts="554c2c2be58d81a5c77b5a2dca03da39d608387c82bc4e5dbdc0cba1837645ae" semantic="b3ec7b2deffaf3c3c23388c2c4847d52984e1061625b5bb1cf8f304f7afcd1e5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `0` ~ `200`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKf -->

<!-- CARROT:MANUAL:BEGIN LongTuningKf -->
<!-- CARROT:REVIEW reviewed-for="b3ec7b2deffaf3c3c23388c2c4847d52984e1061625b5bb1cf8f304f7afcd1e5" reviewed-at="2026-11-11T05:33:10.280724+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the longitudinal feedforward coefficient applied to predicted acceleration requests.

- **Higher:** Increases the contribution of this longitudinal-control term.
- **Lower:** Reduces that contribution.

Volkswagen MEB vehicles, including ID.4, have single-point Kp and Ki tunes, so saved Kp/Ki/Kf settings apply. Updating does not reset previously saved values.
On Ray EV with a detected Comma Pedal and active openpilot longitudinal control, Long Kp/Ki/Kf are visible and their saved values apply to the speed PID. Values load at startup and refresh about once per second during operation.

Other Hyundai/Kia/Genesis configurations fix common Kp/Ki/Kf at 1/0/1. Toyota/Lexus fix them at 0/0/1 because their dedicated vehicle controller corrects acceleration tracking.
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
<!-- CARROT:MANUAL:END LongTuningKf -->

<!-- CARROT:SETTING:END LongTuningKf -->
