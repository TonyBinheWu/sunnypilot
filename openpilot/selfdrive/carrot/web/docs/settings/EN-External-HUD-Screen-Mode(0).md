<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_SCREEN" param="ClusterHudScreenMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Screen Mode(0)

**Menu:** Display \> External HUD \> Screen & Camera

---

<!-- CARROT:SETTING:BEGIN ClusterHudScreenMode -->
<a id="ClusterHudScreenMode"></a>

## External HUD Screen Mode(0)

`ClusterHudScreenMode`

-1: 3D fullscreen 0: Default (navigation/driving report) 1: Debug 2: Debug (system) 3: Debug (graph1) 4: Debug (graph2) 5: Driving Report 6: External navigation fullscreen 7: Driving view + Nav map on right Onroad P prioritizes the parking screen; R shows a reverse reference based on EV6 geometry. Other gears and offroad restore the existing screen mode.

<!-- CARROT:AUTO:BEGIN ClusterHudScreenMode -->
<!-- CARROT:AUTO:SOURCE facts="d87a0de981abe5733884d1c9adcb546640b17ca0f8f8eea54c656c01eb36f4e9" semantic="4454f6bc7bf3c1b0d27dc7adfae91475bc67670dc85dee7fee357a165b54433d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `0`
- **Range:** `-1` ~ `7`
- **Step:** `1`
- **Menu:** Display \> External HUD \> Screen & Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudScreenMode -->

<!-- CARROT:MANUAL:BEGIN ClusterHudScreenMode -->
<!-- CARROT:REVIEW reviewed-for="627a973ecafa1b31a96e570c3d02499497c8b6d45ab1e2366aa65ab21435fe93" reviewed-at="2026-07-31T23:37:31+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `-1` — Uses the full width without an information panel in 3D camera views `0` and `1`. Left-side items retain their margins, right-side gauges and TPMS align to the physical right edge, and the clock, world, and turn signals use the full-display center. In road-camera view `2`, navigation/report selection and panel layout behave exactly like mode `0`.
- `0` — The default screen, showing navigation while it is received and automatically showing the driving report otherwise.
- `1` — General live debug for grouped delay, torque, steering, and lateral-plan state.
- `2` — The reference system screen. It keeps navigation or `NAVI DISCONNECTED` without mode `0`'s automatic report fallback, and uses the route overlay only when no navigation source exists.
- `3` — Disables the driving scene and shows the `ShowPlotMode` graph at large size.
- `4` — Keeps the driving scene and shows the graph in the information panel. Acceleration, steering, fuel, and DEF gauges sit immediately to the graph's left and follow panel swapping; TPMS remains with the driving view.
- `5` — Always shows the driving report.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use `0` for normal automatic navigation/report behavior, `-1` for a wider 3D scene, and `4` to compare the driving scene with the graph. Select `0` to restore the normal automatic screen.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudScreenMode -->

<!-- CARROT:SETTING:END ClusterHudScreenMode -->
