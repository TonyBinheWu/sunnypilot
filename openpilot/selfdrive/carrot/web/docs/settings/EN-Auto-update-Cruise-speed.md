<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_AUTOCRUISE" param="AutoGasSyncSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Auto update Cruise speed

**Menu:** Driving \> Start & Auto \> Auto Cruise

---

<!-- CARROT:SETTING:BEGIN AutoGasSyncSpeed -->
<a id="AutoGasSyncSpeed"></a>

## Auto update Cruise speed

`AutoGasSyncSpeed`

If accelerator is pressed and speed exceeds set speed, update set speed

<!-- CARROT:AUTO:BEGIN AutoGasSyncSpeed -->
<!-- CARROT:AUTO:SOURCE facts="32853013eb45fefaab3838f9d3da87fff0b32d0c5feb3e6a8de136380ed31822" semantic="b7d50e021ae02dfaf5a91c4919bed99b902eecbb6a56c177e5cbdc093c729db0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Start & Auto \> Auto Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasSyncSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasSyncSpeed -->
<!-- CARROT:REVIEW reviewed-for="b7d50e021ae02dfaf5a91c4919bed99b902eecbb6a56c177e5cbdc093c729db0" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** After accelerator input raises vehicle speed above the cruise set speed, raises the set speed to the current speed.
- **Off:** Keeps the existing set speed after accelerator input.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time and compare the cruise activation point and set speed under the same start, accelerator, and lead-vehicle conditions.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasSyncSpeed -->

<!-- CARROT:SETTING:END AutoGasSyncSpeed -->
