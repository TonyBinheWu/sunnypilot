<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_ONNX" param="OnnxBsdEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ONNX Vision BSD

**Menu:** Driving \> Steering \> ONNX Lane & BSD

---

<!-- CARROT:SETTING:BEGIN OnnxBsdEnabled -->
<a id="OnnxBsdEnabled"></a>

## ONNX Vision BSD

`OnnxBsdEnabled`

Enable ONNX camera-based vehicle-side BSD inference from the wide camera. This is independent of lane recognition and defaults to off. It does not affect vehicle-provided BSD.

<!-- CARROT:AUTO:BEGIN OnnxBsdEnabled -->
<!-- CARROT:AUTO:SOURCE facts="52fb469bebb401c799eff1f3850dc6b6b2f2349bc300fb1508a9cf3fef4d4675" semantic="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> ONNX Lane & BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdEnabled -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdEnabled -->
<!-- CARROT:REVIEW reviewed-for="96272d6cd431cbf5a7da6b15e4a4e61a939dbe4357ffcbbc432c06e64be4efbd" reviewed-at="2026-10-20T08:49:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Enabling loads the wide-camera BSD model and alternates across configured sides whose model-estimated lane width is at least 2 m. Disabling unloads the BSD model and clears previous detections while lane classification continues.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Enable `ShareData` so the vision service is running, then use this switch in the ONNX detail screen in Carrot Web. The service checks settings about once per second.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Vehicle-provided BSD is unaffected. Existing lane/BSD users must explicitly enable this separate switch to continue camera BSD.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END OnnxBsdEnabled -->

<!-- CARROT:SETTING:END OnnxBsdEnabled -->
