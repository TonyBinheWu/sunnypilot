<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="LowSpeedSteerReserve" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Low-speed demand follow and response records

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN LowSpeedSteerReserve -->
<a id="LowSpeedSteerReserve"></a>

## Low-speed demand follow and response records

`LowSpeedSteerReserve`

Hyundai/Kia CAN-FD torque only. After 0.30 s sustained demand, allow requested headroom up to 409 at ≤30 km/h and demand-dependent command slew up to 4/4 per 10 ms. Taper at 30–40 km/h; ≥40 uses factory scaling and 2/3. Stored manual values and tuning remain. Records never raise limits. Requires updated Panda firmware, reboot and vehicle validation. For supported EV6/Ioniq 5/Carnival/Sorento variants, HkgPhase1Assist also enables this bounded low-speed path. Turn both switches off to restore stored manual limits. The 2024 Sorento uses the factory torque rise rate in this mode.

<!-- CARROT:AUTO:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:AUTO:SOURCE facts="7c300a3501e166c400c1d96c69c8c3447f9456f3703bca9199b5f3889cbaed27" semantic="05eafe68a23035bc4348334280884728605203a66ac88d3eaa2331b7d736becc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedSteerReserve -->

<!-- CARROT:MANUAL:BEGIN LowSpeedSteerReserve -->
<!-- CARROT:REVIEW reviewed-for="05eafe68a23035bc4348334280884728605203a66ac88d3eaa2331b7d736becc" reviewed-at="2026-11-20T17:30:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Only Hyundai/Kia CAN-FD torque steering is supported. Sustained near-baseline demand for 0.30 s qualifies additional torque up to 409 at ≤30 km/h. The gap to the bounded requested command also selects host increase/decrease limits from factory 2/3 up to 4/4 CAN units per 10 ms; near the target they return to factory rates. Both headroom and extra slew taper over 30–40 km/h; integer commands use discrete steps, and ≥40 km/h uses factory scaling and rates.

Stored CustomSteerMax and CustomSteerDelta values are not overwritten; while enabled, factory normalization remains the baseline. Turning the mode off restores the manual values, but Panda now rejects commands outside its enforced bounds. Gains, live torque tuning and angle-control behavior are not increased by this feature.
The 2024 Sorento builds steering torque at the factory rate in this mode.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Update while parked and complete a restart so the updated Panda firmware and safety parameters load. The optional switch remains below CustomSteerMax and defaults off; after that initial update it is read within about 0.5 s without restarting again. Device > Steering learning progress and Web/APK > Tools > Steering learning progress show current commands, selected slew, target/measured wheel angle and rate, restriction reasons and left/right observed peaks.

Live status expires after 2 s. Saved aggregates are historical, local-only, matched by vehicle/control type and written at most once per 60 s or on exit; no position, route or cloud upload is collected by this recorder.
For supported EV6/Ioniq 5/Carnival/Sorento variants, HkgPhase1Assist also enables this bounded low-speed path. Turn both switches off to restore stored manual limits.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Driver override, invalid CAN, faults, reverse/standstill, stale model or lateral disengagement cancel extra eligibility. Panda independently uses fresh CRC/counter-verified wheel and driver data to bound increases; missing/stale data cannot authorize extra slew. Its original 112-unit/250 ms real-time envelope and request-cut/driver-yield checks remain enforced, including RX-paced replacements. Rapid torque release for driver takeover is preserved.

CAN command slew is neither Nm nor measured wheel angle speed. Observed peaks never become hardware limits or raise control limits; no physical limit probing occurs. Desktop/native checks do not establish vehicle capability. See the [verification scope and remaining baseline failures](https://github.com/TonyBinheWu/sunnypilot/blob/carrot-wip/docs/LOW_SPEED_STEERING_SAFETY.zh-TW.md).
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LowSpeedSteerReserve -->

<!-- CARROT:SETTING:END LowSpeedSteerReserve -->
