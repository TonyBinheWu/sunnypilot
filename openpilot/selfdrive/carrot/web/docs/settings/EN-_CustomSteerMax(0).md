<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="CustomSteerMax" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerMax(0)

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN CustomSteerMax -->
<a id="CustomSteerMax"></a>

## \_CustomSteerMax(0)

`CustomSteerMax`

Maximum Steering Torque — Use the largest value among 270/384/409 that does not cause errors EV6 HDA2 torque steering on the ADAS ECU uses 384 below 11 m/s and 330 from 11 m/s. A lower positive setting caps either band.

<!-- CARROT:AUTO:BEGIN CustomSteerMax -->
<!-- CARROT:AUTO:SOURCE facts="c2967dded24fc3b3a406566d602c5ee424b36a14bff6147e2262e7b33358a5ae" semantic="69a6e47badf874d2955d531c868fbb567fbe47091875499338aed77993a98279" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `30000`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerMax -->

<!-- CARROT:MANUAL:BEGIN CustomSteerMax -->
<!-- CARROT:REVIEW reviewed-for="669ef6b96724cee684584bacd4c6c1cce990b4de53df8969d58d5f175dc0e1ed" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Adjusts the maximum steering-torque limit on supported Hyundai/Kia torque controllers.

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
<!-- CARROT:MANUAL:END CustomSteerMax -->

<!-- CARROT:SETTING:END CustomSteerMax -->
