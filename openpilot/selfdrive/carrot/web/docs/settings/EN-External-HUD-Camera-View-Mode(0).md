<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_SCREEN" param="ClusterHudCameraViewMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Camera View Mode(0)

**Menu:** Display \> External HUD \> Screen & Camera

---

<!-- CARROT:SETTING:BEGIN ClusterHudCameraViewMode -->
<a id="ClusterHudCameraViewMode"></a>

## External HUD Camera View Mode(0)

`ClusterHudCameraViewMode`

0: Default 1: Mode 1 (bottom view) 2: Narrow road camera 3: Wide road camera 4: Automatic narrow/wide camera by speed

<!-- CARROT:AUTO:BEGIN ClusterHudCameraViewMode -->
<!-- CARROT:AUTO:SOURCE facts="2c5faf08a76ea3ee37c834a109a1d01cb2d2d14a8951acf3a22be910898d940a" semantic="af3b40d3730a153e0c5d95a63e09da0dd2f8fe994a2a77fcbd201478e1a2773f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Default (`0`)
- **Range:** Default (`0`) ~ Speed automatic (`4`)
- **Step:** `1`
- **Options:** `0` Default, `1` Bottom view, `2` Narrow camera, `3` Wide camera, `4` Speed automatic
- **Menu:** Display \> External HUD \> Screen & Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudCameraViewMode -->

<!-- CARROT:MANUAL:BEGIN ClusterHudCameraViewMode -->
<!-- CARROT:REVIEW reviewed-for="51f165f147cfa0802afd9fc04c05b0e2a5dbfbeb17f955788f4c25e38081161a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Default
- `1` — Mode 1 (bottom view)
- `2` — Road camera background
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Choose a mode while checking display latency, clarity, and CPU use on the external HUD.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudCameraViewMode -->

<!-- CARROT:SETTING:END ClusterHudCameraViewMode -->
