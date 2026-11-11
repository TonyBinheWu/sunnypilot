<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_LONGTUNE" param="LongTuningKpV" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Long KpV(100)x0.01

**Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning

---

<!-- CARROT:SETTING:BEGIN LongTuningKpV -->
<a id="LongTuningKpV"></a>

## Long KpV(100)x0.01

`LongTuningKpV`

Longitudinal proportional gain for immediate error response. Standard Hyundai, Kia, and Genesis longitudinal control is fixed at Kp 1.0, so this setting is hidden and ignored on those vehicles. Toyota/Lexus fix the common Kp=0 to avoid duplicate correction before their dedicated controller; this setting is hidden and saved values are ignored. An identified Ray EV Comma Pedal configuration exposes this setting and applies the saved value to speed PID within approximately one second.

<!-- CARROT:AUTO:BEGIN LongTuningKpV -->
<!-- CARROT:AUTO:SOURCE facts="c15cb741f3b432869213cc6589137983ce63573b17de7068872b1f4a3592f5d9" semantic="da83b19cd7c1eaed65e221d1571b66a8f33f00b0c83097c2f56007bccd5323c1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `0` ~ `200`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongTuningKpV -->

<!-- CARROT:MANUAL:BEGIN LongTuningKpV -->
<!-- CARROT:REVIEW reviewed-for="da83b19cd7c1eaed65e221d1571b66a8f33f00b0c83097c2f56007bccd5323c1" reviewed-at="2026-11-11T05:33:10.259868+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the longitudinal proportional term that responds immediately to speed error.

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
<!-- CARROT:MANUAL:END LongTuningKpV -->

<!-- CARROT:SETTING:END LongTuningKpV -->
