<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Low-speed model steering reserve

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## Low-speed model steering reserve

`LowSpeedSteerReserve`

Hyundai/Kia CAN-FD torque control only. Sustained demand can use up to 409 below 30 km/h; taper to the baseline at 40 km/h. Preserves CustomSteerMax and baseline scaling. Vehicle validation required.

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="f9c4660750711d42a48a3e4ffcf2cb417007641f52f547ac6b4935bd492de5be" semantic="6a5d981658c4dd294c2fd535015e46b0fe4d8c3e9583fbe6b51bcf29586bdb4d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Only Hyundai/Kia CAN-FD torque steering is supported. Sustained near-baseline demand for 0.30 s can access additional output up to 409 at or below 30 km/h; the target ceiling tapers to the original limit from 30–40 km/h. Ordinary requests keep the original scaling, gains and learned parameters.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

This optional switch is directly below CustomSteerMax and starts off. Changes are read within about 0.5 s without a restart. CustomSteerMax is never overwritten; an existing limit of 409 or higher receives no additional headroom.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Driver intervention, reverse/standstill, invalid CAN, steering faults, missing/stale model data or lateral disengagement remove extra eligibility. Output returns using the existing torque-rate limits, so withdrawal is not instantaneous. EPS angle-request protection and Panda safety limits remain unchanged. This feature has desktop tests only; 409 and the speed thresholds are not validated vehicle capabilities or a guarantee of completing a turn.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
