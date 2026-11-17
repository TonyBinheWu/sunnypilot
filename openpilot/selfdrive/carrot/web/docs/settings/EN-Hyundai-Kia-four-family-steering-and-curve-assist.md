<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="HkgPhase1Assist" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Hyundai Kia four-family steering and curve assist

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN HkgPhase1Assist -->
<a id="HkgPhase1Assist"></a>

## Hyundai Kia four-family steering and curve assist

`HkgPhase1Assist`

Registered EV6, Ioniq 5, Carnival and Sorento platforms only. CAN-FD torque variants reuse bounded low-speed demand follow (up to 409 and 4/4); stored manual limits remain. Angle control and classic Sorento retain existing actuator limits. Small curvature corrections are smoothed progressively at 40–80 km/h; large requests receive less filtering. In direct longitudinal ACC mode, three fresh consecutive model frames qualify a preview curve speed ceiling upstream of MPC. Default off. EPS/Panda guards remain; no emergency avoidance, U-turn or vehicle-performance guarantee. At low speed, same-direction turn-in reduces the existing target filter time constant by up to 40%; return and reversal keep the original filter, with a 30–40 km/h taper. The faster low-speed model-target response applies only to the lane-less model path; custom lane-planner filtering and its delay compensation remain unchanged.

<!-- CARROT:AUTO:BEGIN HkgPhase1Assist -->
<!-- CARROT:AUTO:SOURCE facts="a22be7dc124e3b5829b190a6c3ccdb467cd20bed2ac8da13cafc35ae866f23f3" semantic="1c9c7c054bb743a7a9af0906faec089755f21f0f914e02d4a5b7addd3c56d7c2" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HkgPhase1Assist -->

<!-- CARROT:MANUAL:BEGIN HkgPhase1Assist -->
<!-- CARROT:REVIEW reviewed-for="1c9c7c054bb743a7a9af0906faec089755f21f0f914e02d4a5b7addd3c56d7c2" reviewed-at="2026-11-18T00:00:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Applies only to the registered EV6, Ioniq 5, Carnival and Sorento platforms; existing fingerprint, HDA and torque/angle detection stay authoritative. At low speed, increasing same-direction turn demand reduces the existing target filter time constant by up to 40%, tapering back over 30–40 km/h. Return and reversal retain the original filter. CAN-FD torque variants also reuse LowSpeedSteerReserve with the same qualification, torque ceiling and slew protections. Angle variants and classic Sorento receive no additional actuator authority. At highway speed, small curvature corrections receive additional filtering with at most 0.08 s time constant; larger requests use less filtering. Existing final curvature and actuator limits still apply.
The faster low-speed model-target response applies only to the lane-less model path; custom lane-planner filtering and its delay compensation remain unchanged.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Enable in Driving > Steering > Steering Feel while parked and validate one vehicle configuration at a time. Polling takes about 0.5 s for steering and 1 second for curve assistance. Both this switch and LowSpeedSteerReserve must be off to restore stored manual limits; neither switch overwrites them. Current compatible Panda firmware remains required for the existing low-speed torque path. For a preview curve speed ceiling, direct longitudinal control and lateral control must both be active in ACC mode, with valid vehicle/control/model data and three consecutive new model frames. Stock ACC and blended mode are unchanged. The comfort envelope uses up to 4 seconds of near model geometry, a 2.0 m/s² lateral target and 1.2 m/s² approach budget; its ceiling falls at up to 1.2 m/s per second and releases at 0.5 m/s per second. It is passed to MPC after Carrot speed selection, never raises lower speed or stop targets, and prevents coasting/lead acceleration preview from relaxing curve braking.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Driver pedal/steering input, invalid CAN, steering faults, inactive control, stale/repeated/restarted models or malformed geometry reset the curve ceiling. The added curve feature never requests a stop and does not infer EPS capability from observations. EPS/Panda protection, driver override, request-bit fault prevention, model artifacts and emergency behavior remain unchanged. Desktop tests do not establish real vehicle handling, full-lock/U-turn capability or FSD equivalence.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HkgPhase1Assist -->

<!-- CARROT:SETTING:END HkgPhase1Assist -->
