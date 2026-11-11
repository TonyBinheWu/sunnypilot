<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_ONNX" param="ShareData" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX Lane and BSD Detection

**Menu:** Driving \> Steering \> ONNX Lane & BSD

---

<!-- CARROT:SETTING:BEGIN ShareData -->
<a id="ShareData"></a>

## ONNX Lane and BSD Detection

`ShareData`

Enable on-device lane-type detection. Camera BSD runs only when the separate OnnxBsdEnabled setting is on; it defaults to off and alternates across configured sides whose model-estimated lane width is at least 2 m. Turning this off stops the vision service and preserves vehicle BSD. When enabled, the service starts after onroad initialization and model/CAN/Panda readiness have settled for 0.5 seconds. Engaging cruise is not required. It stops offroad and waits again at the next onroad start.

<!-- CARROT:AUTO:BEGIN ShareData -->
<!-- CARROT:AUTO:SOURCE facts="13c45d979a9ede52011a160f91276e1131a14ad5ab994e8945a89d3bb285a0db" semantic="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> ONNX Lane & BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShareData -->

<!-- CARROT:MANUAL:BEGIN ShareData -->
<!-- CARROT:REVIEW reviewed-for="0ea20987779bff6e6de29f186065d105a554022ef87fd4b93b59b42d499ee336" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When enabled, the comma device classifies camera lane markings and also checks blind spots when `OnnxBsdEnabled` is enabled. Disabling it stops the vision service while preserving vehicle BSD.

- Lane classification runs continuously while camera frames are available.
- With `OnnxBsdEnabled` enabled, camera BSD alternates across configured sides whose model-estimated lane width is at least 2 m. Speed and lane-change direction do not gate detection.

When enabled, the service waits for onroad initialization and model/CAN/Panda readiness to settle for 0.5 seconds. Engaging cruise is not required; it stops offroad and waits again at the next onroad start.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use this switch in Carrot Web. Existing saved values are preserved. Once startup conditions are met, the setting and mici display update within a few seconds.

The mici VISION card shows left/right lane types, the latest processing time, and BSD status. Hiding the camera view still leaves the card and BSD warnings visible.
BSD walls are amber for OEM-only detection, blue for vision-only detection, and light red when both detect. Each side displays its own sources.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

The update includes OpenCV, installed into a local writable directory during normal device startup. No separate pip installation is needed.

BSD standby means that side is not currently being evaluated. No detection does not guarantee the entire blind spot is clear; after disabling the service, its last results disappear when they expire.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END ShareData -->

<!-- CARROT:SETTING:END ShareData -->
