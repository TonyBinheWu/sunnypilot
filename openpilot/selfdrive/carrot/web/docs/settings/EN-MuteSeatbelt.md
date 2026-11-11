<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DM" param="MuteSeatbelt" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# MuteSeatbelt

**Menu:** Vehicle & Hardware \> Driver Monitor

---

<!-- CARROT:SETTING:BEGIN MuteSeatbelt -->
<a id="MuteSeatbelt"></a>

## MuteSeatbelt

`MuteSeatbelt`

MuteSeatbelt

<!-- CARROT:AUTO:BEGIN MuteSeatbelt -->
<!-- CARROT:AUTO:SOURCE facts="7dc96e7cb90fac9c890b7058ed77ce941189c033032cb0fc6063ad1ec7c914a5" semantic="1ebf5b7d58dbd61bfd90f74ebd2f43ac41e416f817f1109e30249922d3cd775e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> Driver Monitor
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MuteSeatbelt -->

<!-- CARROT:MANUAL:BEGIN MuteSeatbelt -->
<!-- CARROT:REVIEW reviewed-for="1ebf5b7d58dbd61bfd90f74ebd2f43ac41e416f817f1109e30249922d3cd775e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Does not add the unlatched-seatbelt state as a driving-blocking event.
- **Off:** Raises the seatbelt-unlatched event when the belt is not fastened.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this while parked, then verify driver monitoring and vehicle warning states on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> When enabled, an unlatched belt is excluded from driving-blocking events. Verify all occupants' seatbelts manually.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MuteSeatbelt -->

<!-- CARROT:SETTING:END MuteSeatbelt -->
