<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DM" param="MuteDoor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# MuteDoor

**Menu:** Vehicle & Hardware \> Driver Monitor

---

<!-- CARROT:SETTING:BEGIN MuteDoor -->
<a id="MuteDoor"></a>

## MuteDoor

`MuteDoor`

MuteDoor

<!-- CARROT:AUTO:BEGIN MuteDoor -->
<!-- CARROT:AUTO:SOURCE facts="00ea196d2c126b86c2271f5e3d328bef08146b3d2d90743ee52352ae86cea5cf" semantic="2e4b627828fbc876d79a4469748d14cb1cd2ea8824c9f737817ecc770bcaf8db" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> Driver Monitor
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MuteDoor -->

<!-- CARROT:MANUAL:BEGIN MuteDoor -->
<!-- CARROT:REVIEW reviewed-for="2e4b627828fbc876d79a4469748d14cb1cd2ea8824c9f737817ecc770bcaf8db" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Does not add the door-open state as a driving-blocking event.
- **Off:** Raises the door-open event when a door is open.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this while parked, then verify driver monitoring and vehicle warning states on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> When enabled, an open door is excluded from driving-blocking events. Verify manually that all doors are closed before moving.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MuteDoor -->

<!-- CARROT:SETTING:END MuteDoor -->
