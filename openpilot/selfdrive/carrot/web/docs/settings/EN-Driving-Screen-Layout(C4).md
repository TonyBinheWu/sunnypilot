<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_BRIGHT" param="ShowModelView" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Driving Screen Layout(C4)

**Menu:** Display \> Brightness & View

---

<!-- CARROT:SETTING:BEGIN ShowModelView -->
<a id="ShowModelView"></a>

## Driving Screen Layout(C4)

`ShowModelView`

Choose camera video and lane/path graphics on the C4 driving screen. Lane/path graphics include lead-vehicle markers. Applies regardless of brightness; changes while driving appear within about 5 seconds. Speed and alerts stay visible even when both are hidden. When an external HUD is connected, On-device Camera with External HUD takes precedence.

<!-- CARROT:AUTO:BEGIN ShowModelView -->
<!-- CARROT:AUTO:SOURCE facts="44503ab1a88690c9b776c1a2a6a0057c44c95641d1966d9362ed4a7cb49497de" semantic="0fbb289950310b907ca1e85a973172fac18f0381fcd7718d1a6f3ebf584a61ce" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** 0 Camera + lanes/path (`0`)
- **Range:** 0 Camera + lanes/path (`0`) ~ 3 Hide both (`3`)
- **Step:** `1`
- **Options:** `0` 0 Camera + lanes/path, `1` 1 Camera only, `2` 2 Lanes/path only, `3` 3 Hide both
- **Menu:** Display \> Brightness & View
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowModelView -->

<!-- CARROT:MANUAL:BEGIN ShowModelView -->
<!-- CARROT:REVIEW reviewed-for="c8040075196baa91f6b37ffa483d6e1197e44f8bd97dd6bfca9c50ab762b41de" reviewed-at="2026-10-08T09:28:59.208385+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Select the video and graphics on the C4 driving screen. Lane/path graphics include lead-vehicle markers.

- `0` — Show lanes/path over camera video.
- `1` — Show camera video only.
- `2` — Show lanes/path on a black background.
- `3` — Hide camera video and lanes/path. Speed, alerts, and driver status stay visible.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

The setting applies regardless of brightness, with no extra wait after entering driving mode. Changes while driving appear within about five seconds without rebooting.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

This setting does not apply to C3/C3X. With an external HUD connected, `ShowCameraWithCluster=0` hides both the on-device camera and lanes/path regardless of this choice.

Camera capture, driving decisions, and vehicle control are unchanged.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ShowModelView -->

<!-- CARROT:SETTING:END ShowModelView -->
