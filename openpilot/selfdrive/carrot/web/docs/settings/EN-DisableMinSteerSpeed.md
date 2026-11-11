<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_START" param="DisableMinSteerSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# DisableMinSteerSpeed

**Menu:** Driving \> Start & Auto \> Engage

---

<!-- CARROT:SETTING:BEGIN DisableMinSteerSpeed -->
<a id="DisableMinSteerSpeed"></a>

## DisableMinSteerSpeed

`DisableMinSteerSpeed`

smdps equiped: 1

<!-- CARROT:AUTO:BEGIN DisableMinSteerSpeed -->
<!-- CARROT:AUTO:SOURCE facts="08d464ada9a9f7e396b22dce0324ca9cbdd554f90ad54a533a96a268b07ad8a0" semantic="1e8fdd77dce60e211fb436b62a63f37b43a57d55ab7b465a438ac1459fdc1ca3" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Start & Auto \> Engage
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DisableMinSteerSpeed -->

<!-- CARROT:MANUAL:BEGIN DisableMinSteerSpeed -->
<!-- CARROT:REVIEW reviewed-for="1e8fdd77dce60e211fb436b62a63f37b43a57d55ab7b465a438ac1459fdc1ca3" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Replaces the vehicle-interface minimum steering speed with `0`.
- **Off:** Keeps the vehicle-specific minimum steering speed.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this while safely parked, then confirm at the next drive start that the steering and cruise states switch as intended.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Use this only on vehicles that physically support low-speed steering, such as supported SMDPS configurations. It does not remove the vehicle's physical or safety limits.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END DisableMinSteerSpeed -->

<!-- CARROT:SETTING:END DisableMinSteerSpeed -->
