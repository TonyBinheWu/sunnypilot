<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_LONGTUNE" param="LongActuatorDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LongActuatorDelay(20)x0.01

**Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning

---

<!-- CARROT:SETTING:BEGIN LongActuatorDelay -->
<a id="LongActuatorDelay"></a>

## LongActuatorDelay(20)x0.01

`LongActuatorDelay`

Longitudinal Delay Value (Higher values lead to earlier acceleration/deceleration) — HKG: 20 Recommeded

<!-- CARROT:AUTO:BEGIN LongActuatorDelay -->
<!-- CARROT:AUTO:SOURCE facts="105a480bf7b399fbd639f2a5ab7bdb728b19c0f83993b50c83571547ae347b53" semantic="83f945e2bbe7928bc6258df845c0f2c9ea2701fa8ecf7a6225873c62d3a181cc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `20`
- **Range:** `0` ~ `200`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Accel/Brake Tuning
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LongActuatorDelay -->

<!-- CARROT:MANUAL:BEGIN LongActuatorDelay -->
<!-- CARROT:REVIEW reviewed-for="83f945e2bbe7928bc6258df845c0f2c9ea2701fa8ecf7a6225873c62d3a181cc" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Compensates for delay between acceleration or braking requests and vehicle response.

- **Higher:** Assumes more longitudinal delay and requests target changes earlier.
- **Lower:** Reduces longitudinal lead compensation.
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
<!-- CARROT:MANUAL:END LongActuatorDelay -->

<!-- CARROT:SETTING:END LongActuatorDelay -->
