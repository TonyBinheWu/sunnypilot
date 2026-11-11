<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_RADAR" param="ClusterHudRadarInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Radar Info(4)

**Menu:** Display \> External HUD \> Radar Display

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarInfo -->
<a id="ClusterHudRadarInfo"></a>

## External HUD Radar Info(4)

`ClusterHudRadarInfo`

0: Off 1: Speed (vehicles only) 2: Speed, distance (vehicles only) 3: Speed (all) 4: Speed, distance (all)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarInfo -->
<!-- CARROT:AUTO:SOURCE facts="4a6ce1e4e2c58d4144b2c5835e76807e317ad71645a72887e47b86031987fab7" semantic="05cc3268420daab3de56e5bbd791d233fe6c5cccda542fd4688e6a5bd63dfa2a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `4`
- **Range:** `0` ~ `4`
- **Step:** `1`
- **Menu:** Display \> External HUD \> Radar Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarInfo -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarInfo -->
<!-- CARROT:REVIEW reviewed-for="05cc3268420daab3de56e5bbd791d233fe6c5cccda542fd4688e6a5bd63dfa2a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Off
- `1` — Speed (vehicles only)
- `2` — Speed, distance (vehicles only)
- `3` — Speed (all)
- `4` — Speed, distance (all)
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On the external HUD, observe the same lead and surrounding objects to verify displayed targets, distance, and source distinction.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarInfo -->

<!-- CARROT:SETTING:END ClusterHudRadarInfo -->
