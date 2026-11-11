<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_PERF" param="ClusterHudDebug" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Debug(0)

**Menu:** Display \> External HUD \> Performance & Debug

---

<!-- CARROT:SETTING:BEGIN ClusterHudDebug -->
<a id="ClusterHudDebug"></a>

## External HUD Debug(0)

`ClusterHudDebug`

0: Onroad only 1: Always 2: Always + UI 3: Always + Navi

<!-- CARROT:AUTO:BEGIN ClusterHudDebug -->
<!-- CARROT:AUTO:SOURCE facts="0d9229b829c0f201fb996d55d05e51dd8653726197fd540dc47c3e19da781473" semantic="f3690826c5fa0e74264bedafa8192c8a74e880f3190c33ebf87d9b5748bcdf27" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Display \> External HUD \> Performance & Debug
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudDebug -->

<!-- CARROT:MANUAL:BEGIN ClusterHudDebug -->
<!-- CARROT:REVIEW reviewed-for="f3690826c5fa0e74264bedafa8192c8a74e880f3190c33ebf87d9b5748bcdf27" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Onroad only
- `1` — Always
- `2` — Always + UI
- `3` — Always + Navi
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time only for diagnosis and verify external-HUD frame stability and system load.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudDebug -->

<!-- CARROT:SETTING:END ClusterHudDebug -->
