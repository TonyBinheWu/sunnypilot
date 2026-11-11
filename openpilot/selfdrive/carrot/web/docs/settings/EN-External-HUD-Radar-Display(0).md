<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_RADAR" param="ClusterHudRadarDisplay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Radar Display(0)

**Menu:** Display \> External HUD \> Radar Display

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarDisplay -->
<a id="ClusterHudRadarDisplay"></a>

## External HUD Radar Display(0)

`ClusterHudRadarDisplay`

0: Default (merge nearby radar points) 1: Detail (raw radar points)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarDisplay -->
<!-- CARROT:AUTO:SOURCE facts="635f1c1f5853ac8b5547617b63f810a8bff13caf400a7220b4ac6e5dbd712959" semantic="c0542f70ce7ff639693facf6fed2c23f3d14b8dd10885a9e546818549e5afdce" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Display \> External HUD \> Radar Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarDisplay -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarDisplay -->
<!-- CARROT:REVIEW reviewed-for="c0542f70ce7ff639693facf6fed2c23f3d14b8dd10885a9e546818549e5afdce" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Default (merge nearby radar points)
- `1` — Detail (raw radar points)
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On the external HUD, observe the same lead and surrounding objects to verify displayed targets, distance, and source distinction.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarDisplay -->

<!-- CARROT:SETTING:END ClusterHudRadarDisplay -->
