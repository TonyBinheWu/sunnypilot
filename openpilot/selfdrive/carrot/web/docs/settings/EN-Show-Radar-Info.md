<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowRadarInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Radar Info

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowRadarInfo -->
<a id="ShowRadarInfo"></a>

## Show Radar Info

`ShowRadarInfo`

0:None,1:display,2:+relative pos, 3:stopped obstacle

<!-- CARROT:AUTO:BEGIN ShowRadarInfo -->
<!-- CARROT:AUTO:SOURCE facts="2853a7cf7555a3359bcd22c894f66167df425c286e13f604f4d2637f0ce8e8b4" semantic="fb6304349c3a0b1cfa84b4b40b7437938cd0f850a9949f10e2c90253a72c5c3d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowRadarInfo -->

<!-- CARROT:MANUAL:BEGIN ShowRadarInfo -->
<!-- CARROT:REVIEW reviewed-for="fb6304349c3a0b1cfa84b4b40b7437938cd0f850a9949f10e2c90253a72c5c3d" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — None
- `1` — display
- `2` — +relative pos
- `3` — stopped obstacle

On the standard device driving screen for RAV4 2022 with the ARS display stream, `3` also displays adjacent-lane objects separately from control leads. Moving objects show speed, and slow or stationary objects show a star; a visible object is not necessarily a braking target.

CRC, object-age, speed-validity and range conditions remain. Stale, invalid or empty input clears the display. Modes `1` and `2`, other receivers, and web/mici screens keep their existing path. This does not add Toyota side-corner radar support.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check placement and readability on the driving display and enable only the information you need.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowRadarInfo -->

<!-- CARROT:SETTING:END ShowRadarInfo -->
