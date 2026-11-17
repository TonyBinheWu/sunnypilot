<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Low-speed demand follow and response records

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## Low-speed demand follow and response records

`LowSpeedSteerReserve`

Hyundai/Kia CAN-FD torque control only. After 0.30 s sustained demand, allow only requested headroom up to 409 at ≤30 km/h; taper at 30–40 km/h. When enabled, factory scaling and slew rates apply at all speeds; manual values stay stored. Passive records never raise limits. Vehicle validation required.

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="d0f0af903bbd1277178b8adefd2bf5bd85fdf15c4f7de067e2f02fa4cfa3183f" semantic="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="f3e6e9a5914e7a8cb28bed45e8f14db13132a0c4aeea40956275b3c4dffe4bba" reviewed-at="2026-11-17T12:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Only Hyundai/Kia CAN-FD torque steering is supported. After 0.30 s of sustained near-baseline demand, allow only requested headroom up to 409 at ≤30 km/h; taper the ceiling from 30–40 km/h and use the factory limit at ≥40 km/h. While enabled, factory normalization and factory increase/decrease rates apply at every speed; stored CustomSteerMax and CustomSteerDelta values are ignored during operation but not overwritten. Gains and live torque tuning stay unchanged. Angle-control vehicles receive no additional authority.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

The optional switch remains directly below CustomSteerMax. It is read within about 0.5 s without restarting; turning it off restores the stored manual limits. Device > Steering learning progress and Web/APK > Tools > Steering learning progress show requested/sent commands, target/measured wheel angle, measured angle rate, current restriction, and left/right observed peaks. Fresh status expires after 2 s; saved aggregates are explicitly historical and reload only for a matching vehicle/control type. Only enabled-mode aggregates are collected locally, saved at most once per 60 s and on control/mode exit; no location, route or cloud upload is included.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Driver override, invalid CAN, faults, reverse/standstill, stale model or lateral disengagement cancel extra eligibility. Withdrawal follows factory slew limits; EPS request protection and Panda safety remain unchanged. Commands are CAN units, not Nm; increase/decrease values mean CAN units per 10 ms, not wheel angle speed. Observed peaks and tracking errors do not identify physical EPS limits and never raise control limits or trigger limit probing. This feature has desktop tests only; actual vehicle validation is still required.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
