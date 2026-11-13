<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable Carrot Vision

**Menu:** Vehicle & Hardware \> Driver Monitor

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## Enable Carrot Vision

`CarrotVisionEnabled`

Enables web road video, including parked viewing. Camera and dedicated encoder are requested only for a viewing session and released afterward, independently of driver monitoring and the external HUD. Simultaneous video use may increase device load.

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="2e36a8334deed4a61ecb6e049ec9c02b215bd7e80f28b050c43ed520b0a4f65e" semantic="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Off (`0`)
- **Range:** Off (`0`) ~ On (`1`)
- **Step:** `1`
- **Options:** `0` Off, `1` On
- **Menu:** Vehicle & Hardware \> Driver Monitor
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotVisionEnabled -->

<!-- CARROT:MANUAL:BEGIN CarrotVisionEnabled -->
<!-- CARROT:REVIEW reviewed-for="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" reviewed-at="2026-11-13T16:58:12Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Enables road video while driving or parked, independently of driver monitoring and the external HUD. Parked camera and encoder demand exists only while a viewing session remains; other camera owners retain their own conditions.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Enable this setting and open Vision in the app or web page. Update vehicle software and reboot once; CarrotAssist 0.2.16 remains compatible and a diagnostic camera runner is not needed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Parked viewing does not start driving models, controls or normal driving recording, and does not reuse old driving guidance; recorded replay retains recorded data. Battery shutdown rules remain. The old DisableDM video choice migrates once without changing driver monitoring or experimental mode.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
