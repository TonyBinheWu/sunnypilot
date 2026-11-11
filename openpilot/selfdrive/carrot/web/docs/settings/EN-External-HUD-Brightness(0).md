<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_BASIC" param="ClusterHudBrightness" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Brightness(0)

**Menu:** Display \> External HUD \> Basic

---

<!-- CARROT:SETTING:BEGIN ClusterHudBrightness -->
<a id="ClusterHudBrightness"></a>

## External HUD Brightness(0)

`ClusterHudBrightness`

0: Auto 1-100: Brightness

<!-- CARROT:AUTO:BEGIN ClusterHudBrightness -->
<!-- CARROT:AUTO:SOURCE facts="f1f8da1a2c7cdcff42bbf0ff5930ba2d9f5f4af459a2421f76c542343a891bb0" semantic="22a87e6cddc1752b7b1eeb6748de1b1b2c63a65f6e171b170e1ca2b1f17a1ece" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `0%` ~ `100%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Display \> External HUD \> Basic
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudBrightness -->

<!-- CARROT:MANUAL:BEGIN ClusterHudBrightness -->
<!-- CARROT:REVIEW reviewed-for="22a87e6cddc1752b7b1eeb6748de1b1b2c63a65f6e171b170e1ca2b1f17a1ece" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Uses automatic brightness. If the connected main-screen brightness is unavailable, the external-HUD default is used.
- `1`–`100` — Fixes external-HUD brightness to that percentage.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this with the external HUD connected, then verify orientation, brightness, and map connection.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudBrightness -->

<!-- CARROT:SETTING:END ClusterHudBrightness -->
