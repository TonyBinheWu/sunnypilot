<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="LatSuspendAngleDeg" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AutoSteering Suspend Angle(300)

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN LatSuspendAngleDeg -->
<a id="LatSuspendAngleDeg"></a>

## AutoSteering Suspend Angle(300)

`LatSuspendAngleDeg`

Auto steering pauses at large steering angles and resumes when it returns within 15.

<!-- CARROT:AUTO:BEGIN LatSuspendAngleDeg -->
<!-- CARROT:AUTO:SOURCE facts="f544aea5cf06b3a7373d86145253d506658e95323c15f3e7e46b5df15dd9a3e1" semantic="6a5eddcf99410a800bf67cddd5eed9ce00f5be22d98b8e33bcfaec45e132a42b" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `300`
- **Range:** `45` ~ `300`
- **Step:** `10`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatSuspendAngleDeg -->

<!-- CARROT:MANUAL:BEGIN LatSuspendAngleDeg -->
<!-- CARROT:REVIEW reviewed-for="6a5eddcf99410a800bf67cddd5eed9ce00f5be22d98b8e33bcfaec45e132a42b" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Auto steering pauses at large steering angles and resumes when it returns within 15.

- **Higher:** Starts driver-steering suspension at a larger steering angle.
- **Lower:** Suspends earlier at a smaller angle.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use small, one-at-a-time changes on the same straight and gentle curve, checking delay, oscillation, and recovery after driver input.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatSuspendAngleDeg -->

<!-- CARROT:SETTING:END LatSuspendAngleDeg -->
