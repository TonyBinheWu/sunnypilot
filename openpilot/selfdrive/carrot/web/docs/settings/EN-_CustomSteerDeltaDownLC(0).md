<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaDownLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerDeltaDownLC(0)

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaDownLC -->
<a id="CustomSteerDeltaDownLC"></a>

## \_CustomSteerDeltaDownLC(0)

`CustomSteerDeltaDownLC`

Torque Vehicle — Temporarily applies SteerDeltaDown during lane changes EV6 HDA2 torque steering on the ADAS ECU uses a fixed withdrawal rate of 3 units per 10 ms, including driver override.

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:AUTO:SOURCE facts="6499a805f917de0ec6589ba10dd495e0e0c8866011760876048e307140c07d62" semantic="24f993369a8dc843e97c8b377086b40d1cb55d05c6cdf714f2e9f859ab68ba73" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `50`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaDownLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaDownLC -->
<!-- CARROT:REVIEW reviewed-for="a336e35a09a15ab311502cba35f76a68aa166dc74ce982901b724dd1b69de65e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Torque Vehicle — Temporarily applies SteerDeltaDown during lane changes.

- **Higher:** Increases the applicable steering-torque limit or rate.
- **Lower:** Reduces the limit or rate.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On supported torque-control vehicles, adjust one item at a time and verify steering ramp-up and ramp-down in normal driving and lane changes.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSteerDeltaDownLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaDownLC -->
