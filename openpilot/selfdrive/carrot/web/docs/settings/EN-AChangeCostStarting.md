<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_STOPGO" param="AChangeCostStarting" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AChangeCostStarting

**Menu:** Driving \> Cruise & Gap \> Stop & Resume

---

<!-- CARROT:SETTING:BEGIN AChangeCostStarting -->
<a id="AChangeCostStarting"></a>

## AChangeCostStarting

`AChangeCostStarting`

AccelCost Starting, 0:rapid starting

<!-- CARROT:AUTO:BEGIN AChangeCostStarting -->
<!-- CARROT:AUTO:SOURCE facts="a4361bb150d95ad771f44ddb234bfc2f7fd840ca96a49e6ac63e544ed7aae93b" semantic="66fd2bf8a16210234cb0ec52d03ef432cc413d2ec880fd815f8fb436da528c88" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `10`
- **Range:** `0` ~ `200`
- **Step:** `10`
- **Menu:** Driving \> Cruise & Gap \> Stop & Resume
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AChangeCostStarting -->

<!-- CARROT:MANUAL:BEGIN AChangeCostStarting -->
<!-- CARROT:REVIEW reviewed-for="66fd2bf8a16210234cb0ec52d03ef432cc413d2ec880fd815f8fb436da528c88" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Adjusts the acceleration-change penalty during launch.

- **Higher:** Penalizes acceleration change more during launch.
- **Lower:** Allows faster launch acceleration.
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
<!-- CARROT:MANUAL:END AChangeCostStarting -->

<!-- CARROT:SETTING:END AChangeCostStarting -->
