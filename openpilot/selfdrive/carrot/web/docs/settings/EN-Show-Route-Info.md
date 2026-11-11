<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowRouteInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Route Info

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowRouteInfo -->
<a id="ShowRouteInfo"></a>

## Show Route Info

`ShowRouteInfo`

Operates only when connected to APN. 0: Off, 1: On

<!-- CARROT:AUTO:BEGIN ShowRouteInfo -->
<!-- CARROT:AUTO:SOURCE facts="3076c5ab3a876fa847569082ca433629d71d7a041fbe132edea6954b84418b23" semantic="d6624b9f6b4c43ab8c8df641e79f08306b4f0a603d2f3e19ef6508dcf38b41b0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowRouteInfo -->

<!-- CARROT:MANUAL:BEGIN ShowRouteInfo -->
<!-- CARROT:REVIEW reviewed-for="d6624b9f6b4c43ab8c8df641e79f08306b4f0a603d2f3e19ef6508dcf38b41b0" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The current `carrot-wip` runtime has no consumer for this parameter, so changing it does not alter the driving display.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

There is currently nothing to adjust or verify while driving because the runtime does not consume this setting.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowRouteInfo -->

<!-- CARROT:SETTING:END ShowRouteInfo -->
