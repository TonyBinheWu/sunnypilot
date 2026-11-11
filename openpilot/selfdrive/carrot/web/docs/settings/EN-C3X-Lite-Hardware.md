<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DEVICE" param="HardwareC3xLite" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# C3X Lite Hardware

**Menu:** Vehicle & Hardware \> Device Hardware

---

<!-- CARROT:SETTING:BEGIN HardwareC3xLite -->
<a id="HardwareC3xLite"></a>

## C3X Lite Hardware

`HardwareC3xLite`

Enable only on C3X Lite. Uses the GPIO buzzer instead of the speaker/amplifier and disables audio and logging processes. Reboot the device after changing.

<!-- CARROT:AUTO:BEGIN HardwareC3xLite -->
<!-- CARROT:AUTO:SOURCE facts="43ccb404f8034b15e4b388ebcd38fdd1387ba669050ddb0b4fd812a417bff575" semantic="1d1f4a2f5d6f90a2445f2e04e4f643f09e565be8708d71ac3d2190980ba0455c" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> Device Hardware
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HardwareC3xLite -->

<!-- CARROT:MANUAL:BEGIN HardwareC3xLite -->
<!-- CARROT:REVIEW reviewed-for="1d1f4a2f5d6f90a2445f2e04e4f643f09e565be8708d71ac3d2190980ba0455c" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Enable only on C3X Lite. Uses the GPIO buzzer instead of the speaker/amplifier and disables audio and logging processes. Reboot the device after changing.
- **Off:** Does not apply this feature and keeps the existing behavior.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this only when the device hardware matches exactly, then reboot and verify sound, logging, and process state.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> Enabling this on a standard device can disable audio and logging processes. Reboot the device after changing it.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HardwareC3xLite -->

<!-- CARROT:SETTING:END HardwareC3xLite -->
