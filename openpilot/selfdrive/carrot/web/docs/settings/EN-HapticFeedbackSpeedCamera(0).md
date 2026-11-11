<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_HYUNDAI" param="HapticFeedbackWhenSpeedCamera" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# HapticFeedbackSpeedCamera(0)

**Menu:** Vehicle & Hardware \> Hyundai·Kia

---

<!-- CARROT:SETTING:BEGIN HapticFeedbackWhenSpeedCamera -->
<a id="HapticFeedbackWhenSpeedCamera"></a>

## HapticFeedbackSpeedCamera(0)

`HapticFeedbackWhenSpeedCamera`

0: Disabled, 1: Vibration, 2: Instrument Cluster, 3: HUD Display

<!-- CARROT:AUTO:BEGIN HapticFeedbackWhenSpeedCamera -->
<!-- CARROT:AUTO:SOURCE facts="f1c6656b7bd9775832eba35dda8f652a8df3d951bd6cba1fee86ce57f589245e" semantic="e9e7ad9d957bc03d8cb260062ab40a0f6d2de683d9c3d9106ea39f476072aad3" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Vehicle & Hardware \> Hyundai·Kia
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HapticFeedbackWhenSpeedCamera -->

<!-- CARROT:MANUAL:BEGIN HapticFeedbackWhenSpeedCamera -->
<!-- CARROT:REVIEW reviewed-for="e9e7ad9d957bc03d8cb260062ab40a0f6d2de683d9c3d9106ea39f476072aad3" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Disabled
- `1` — Vibration
- `2` — Instrument Cluster
- `3` — HUD Display
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Confirm the vehicle specification and harness configuration, configure while parked, and verify SCC and lane-warning behavior on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> A mismatched vehicle, model year, HDA generation, or harness location can cause incorrect SCC or longitudinal behavior.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HapticFeedbackWhenSpeedCamera -->

<!-- CARROT:SETTING:END HapticFeedbackWhenSpeedCamera -->
