<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_ONNX" param="OnnxLaneThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Lane Confidence Threshold

**Menu:** Driving \> Steering \> ONNX Lane & BSD

---

<!-- CARROT:SETTING:BEGIN OnnxLaneThreshold -->
<a id="OnnxLaneThreshold"></a>

## Lane Confidence Threshold

`OnnxLaneThreshold`

Minimum confidence required to accept a solid or dashed lane candidate.

<!-- CARROT:AUTO:BEGIN OnnxLaneThreshold -->
<!-- CARROT:AUTO:SOURCE facts="3d83b08609039d2756ef1d11c0729af05db2de8b1bd45af6ab66a19135f97160" semantic="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `25%`
- **Range:** `0%` ~ `100%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Driving \> Steering \> ONNX Lane & BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxLaneThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxLaneThreshold -->
<!-- CARROT:REVIEW reviewed-for="9b6f0e804d5db37092712a2e6f8da749a11d144884d9d3e3ab707e7f49372c32" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Raising this value accepts lane classifications only at higher confidence; lowering it accepts more uncertain classifications.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxLaneThreshold -->

<!-- CARROT:SETTING:END OnnxLaneThreshold -->
