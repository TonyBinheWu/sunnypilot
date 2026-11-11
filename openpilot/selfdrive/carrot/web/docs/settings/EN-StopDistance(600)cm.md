<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_STOPGO" param="StopDistanceCarrot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# StopDistance(600)cm

**Menu:** Driving \> Cruise & Gap \> Stop & Resume

---

<!-- CARROT:SETTING:BEGIN StopDistanceCarrot -->
<a id="StopDistanceCarrot"></a>

## StopDistance(600)cm

`StopDistanceCarrot`

Stop Distance \* 0.8

<!-- CARROT:AUTO:BEGIN StopDistanceCarrot -->
<!-- CARROT:AUTO:SOURCE facts="7cdd8af4705561d05db47357ae6bb58f755fa12c0e1d287906337a6f7887d472" semantic="828f04295b09ba58b2345b32de89023747b2e835cd5f40e45378caea5d4fc7d8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `600cm`
- **Range:** `400cm` ~ `1000cm`
- **Step:** `10`
- **Display unit:** `cm`
- **Menu:** Driving \> Cruise & Gap \> Stop & Resume
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END StopDistanceCarrot -->

<!-- CARROT:MANUAL:BEGIN StopDistanceCarrot -->
<!-- CARROT:REVIEW reviewed-for="828f04295b09ba58b2345b32de89023747b2e835cd5f40e45378caea5d4fc7d8" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Sets the base stopping buffer used by longitudinal MPC for leads and stop obstacles.

- **Higher:** Increases the target stopping and following buffer.
- **Lower:** Reduces the target buffer.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Adjust one item at a time under the same lead-vehicle stop-and-go condition, checking final stop position and restart response.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END StopDistanceCarrot -->

<!-- CARROT:SETTING:END StopDistanceCarrot -->
