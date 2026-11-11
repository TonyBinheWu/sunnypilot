<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_RADAR" param="ClusterHudRadarSourceColor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Radar Source Colors(0)

**Menu:** Display \> External HUD \> Radar Display

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarSourceColor -->
<a id="ClusterHudRadarSourceColor"></a>

## External HUD Radar Source Colors(0)

`ClusterHudRadarSourceColor`

0: Default (all vehicles gray) 1: On (SCC=R, HDA=B, RADAR=O)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarSourceColor -->
<!-- CARROT:AUTO:SOURCE facts="aa07073840f9752c2f88b49d085edc74ce6a277677dd723728e74c5e62a7b10b" semantic="e1a4577beb594b1aee54203a64b4d871bb2dcc847004a709ddfd411c1a3f15b9" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Display \> External HUD \> Radar Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarSourceColor -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarSourceColor -->
<!-- CARROT:REVIEW reviewed-for="e1a4577beb594b1aee54203a64b4d871bb2dcc847004a709ddfd411c1a3f15b9" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Default (all vehicles gray)
- `1` — On (SCC=R, HDA=B, RADAR=O)
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On the external HUD, observe the same lead and surrounding objects to verify displayed targets, distance, and source distinction.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarSourceColor -->

<!-- CARROT:SETTING:END ClusterHudRadarSourceColor -->
