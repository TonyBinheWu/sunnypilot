<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_BASIC" param="ClusterNaviMapFps" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cluster Navi Map FPS(1)

**Menu:** Display \> External HUD \> Basic

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapFps -->
<a id="ClusterNaviMapFps"></a>

## Cluster Navi Map FPS(1)

`ClusterNaviMapFps`

0: 5 FPS 1: 10 FPS (default) 2: 20 FPS 3: 30 FPS This is independent of HUD FPS and map bitrate is selected automatically. The external navigation app reconnects automatically when changed.

<!-- CARROT:AUTO:BEGIN ClusterNaviMapFps -->
<!-- CARROT:AUTO:SOURCE facts="2296a69e831984be62cfad3894121bebe11e2c59754f72f8e296ee970ea7e9d2" semantic="e37c29337d96679ca12cd545db724e093fed073e51e81b87e087206f74a837b1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** 10 FPS (`1`)
- **Range:** 5 FPS (`0`) ~ 30 FPS (`3`)
- **Step:** `1`
- **Options:** `0` 5 FPS, `1` 10 FPS, `2` 20 FPS, `3` 30 FPS
- **Menu:** Display \> External HUD \> Basic
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapFps -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapFps -->
<!-- CARROT:REVIEW reviewed-for="60a988eea43a59afc28a79f8db4eb165d0c12f35d06be7d5355a8d51c79c7451" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — 5 FPS
- `1` — 10 FPS (default)
- `2` — 20 FPS
- `3` — 30 FPS / This is independent of HUD FPS and map bitrate is selected automatically. / The external navigation app reconnects automatically when changed
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this with the external HUD connected, then verify orientation, brightness, and map connection.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> Map FPS is independent of the main HUD FPS, and map bitrate is selected automatically for the chosen rate. Changing it reconnects external navigation.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ClusterNaviMapFps -->

<!-- CARROT:SETTING:END ClusterNaviMapFps -->
