<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_PATH" param="RainbowMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Rainbow Road (SP style)

**Menu:** Display \> Path Display

---

<!-- CARROT:SETTING:BEGIN RainbowMode -->
<a id="RainbowMode"></a>

## Rainbow Road (SP style)

`RainbowMode`

Show an animated SP-style rainbow on the predicted path while lateral control is active. 0:Off, 1:On. Display only; steering, speed and path calculation are unchanged. Applies without restarting.

<!-- CARROT:AUTO:BEGIN RainbowMode -->
<!-- CARROT:AUTO:SOURCE facts="5a34484bb0ee76cd328ad48761ce9e211b382cf10bae1ce9e95b5ac7ca0ad5e4" semantic="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Display \> Path Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RainbowMode -->

<!-- CARROT:MANUAL:BEGIN RainbowMode -->
<!-- CARROT:REVIEW reviewed-for="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" reviewed-at="2026-11-15T15:32:10.472809+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When enabled and lateral control is active, the on-device predicted path uses an animated rainbow gradient inspired by SP. When disabled or lateral control is inactive, the existing path style is used.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use the device Toggles screen, or search for `RainbowMode` in Carrot Web / CarrotAssist. The setting applies without restarting on C3/C3X and C4. Existing path modes and colors are restored when disabled.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

This only changes the path fill. Steering, cruise speed, model output and alerts are unchanged. The web / APK rainbow presentation has its own `vision_rainbow_lane` preference.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END RainbowMode -->

<!-- CARROT:SETTING:END RainbowMode -->
