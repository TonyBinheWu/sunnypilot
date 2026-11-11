<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowDeviceState" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Device Info

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowDeviceState -->
<a id="ShowDeviceState"></a>

## Show Device Info

`ShowDeviceState`

Show Device Info

<!-- CARROT:AUTO:BEGIN ShowDeviceState -->
<!-- CARROT:AUTO:SOURCE facts="650ba8ddf26f1de547280b65238751c6fdead7679c7e0cc26c6ae4086167de31" semantic="8a73859d7671881ac742cd8ff077a0351b890d70d1b91e02acafa07a24cebf7a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `1`
- **Range:** `0` ~ `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowDeviceState -->

<!-- CARROT:MANUAL:BEGIN ShowDeviceState -->
<!-- CARROT:REVIEW reviewed-for="8a73859d7671881ac742cd8ff077a0351b890d70d1b91e02acafa07a24cebf7a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Shows device state such as CPU temperature and memory use in the driving HUD.
- **Off:** Hides device state and uses the smaller HUD information box.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check placement and readability on the driving display and enable only the information you need.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowDeviceState -->

<!-- CARROT:SETTING:END ShowDeviceState -->
