<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_SW" param="SoftwareMenu" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable Software menu

**Menu:** System \> Software

---

<!-- CARROT:SETTING:BEGIN SoftwareMenu -->
<a id="SoftwareMenu"></a>

## Enable Software menu

`SoftwareMenu`

Turn off on memory error

<!-- CARROT:AUTO:BEGIN SoftwareMenu -->
<!-- CARROT:AUTO:SOURCE facts="fdcef19fca9c50224bfd1c5ee205fe5fcdac2aa68ebed14f2f8bc82582b8567b" semantic="faefc012a681c0434720425d608a2393574213ba2bcc32f6be3bf2d32e939dff" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** System \> Software
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoftwareMenu -->

<!-- CARROT:MANUAL:BEGIN SoftwareMenu -->
<!-- CARROT:REVIEW reviewed-for="faefc012a681c0434720425d608a2393574213ba2bcc32f6be3bf2d32e939dff" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Runs the software-update process while offroad and shows the Software group in Carrot Web.
- **Off:** Does not run the update process and hides that group.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this while offroad, then reopen Carrot Web and verify both Software-group visibility and updater-process state.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> This is a process-configuration setting for memory-problem diagnosis. Keep the default for normal use.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SoftwareMenu -->

<!-- CARROT:SETTING:END SoftwareMenu -->
