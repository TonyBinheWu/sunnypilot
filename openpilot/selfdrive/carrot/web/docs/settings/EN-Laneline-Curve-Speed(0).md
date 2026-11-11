<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="UseLaneLineCurveSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Laneline: Curve Speed(0)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN UseLaneLineCurveSpeed -->
<a id="UseLaneLineCurveSpeed"></a>

## Laneline: Curve Speed(0)

`UseLaneLineCurveSpeed`

LaneMode is not used below the set speed

<!-- CARROT:AUTO:BEGIN UseLaneLineCurveSpeed -->
<!-- CARROT:AUTO:SOURCE facts="6966e389a5e0e3a77c728a8efcb8935bba3fee9f3fbd599e38861075d8174c96" semantic="ba0eea8757a1b91d43653961d6c80ce6c8384ba9524d5ee91a71df24e30beb5e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0km/h`
- **Range:** `0km/h` ~ `200km/h`
- **Step:** `10`
- **Display unit:** `km/h`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseLaneLineCurveSpeed -->

<!-- CARROT:MANUAL:BEGIN UseLaneLineCurveSpeed -->
<!-- CARROT:REVIEW reviewed-for="ba0eea8757a1b91d43653961d6c80ce6c8384ba9524d5ee91a71df24e30beb5e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

LaneMode is not used below the set speed.

- **Higher:** Raises the applicable speed or speed threshold.
- **Lower:** Lowers the speed or threshold.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Repeat the same lane and curve while adjusting one item at a time, comparing path tracking, steering response, and smoothness together.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END UseLaneLineCurveSpeed -->

<!-- CARROT:SETTING:END UseLaneLineCurveSpeed -->
