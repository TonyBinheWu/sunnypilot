<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaDown" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerDeltaDown(0)

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaDown -->
<a id="CustomSteerDeltaDown"></a>

## \_CustomSteerDeltaDown(0)

`CustomSteerDeltaDown`

Torque Vehicle — Higher values increase steering wheel release speed EV6 HDA2 torque steering on the ADAS ECU uses a fixed withdrawal rate of 3 units per 10 ms, including driver override.

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaDown -->
<!-- CARROT:AUTO:SOURCE facts="4f755fc485ffccc66fc1bf2ea8594c4545356028fbc26c6df5b3a1c3d8a61fbb" semantic="a804ff8b309581e89bebde4f8a28234c43931ae219c283217df3cfec42cf2e44" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `50`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaDown -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaDown -->
<!-- CARROT:REVIEW reviewed-for="3a4631b4c069572270462f11246712d178942f087b84cb31aae626aefbbeb3b8" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Torque Vehicle — Higher values increase steering wheel release speed.

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
<!-- CARROT:MANUAL:END CustomSteerDeltaDown -->

<!-- CARROT:SETTING:END CustomSteerDeltaDown -->
