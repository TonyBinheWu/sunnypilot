<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_ONNX" param="OnnxBsdSmoothingMs" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# BSD Hold Time

**Menu:** Driving \> Steering \> ONNX Lane & BSD

---

<!-- CARROT:SETTING:BEGIN OnnxBsdSmoothingMs -->
<a id="OnnxBsdSmoothingMs"></a>

## BSD Hold Time

`OnnxBsdSmoothingMs`

Smooths BSD confidence; an active warning clears 15 percentage points below its activation threshold.

<!-- CARROT:AUTO:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:AUTO:SOURCE facts="c7cae7fff0027addb2261106c8a30b6fa40796c134620f12fdba9941feb98107" semantic="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `200ms`
- **Range:** `100ms` ~ `500ms`
- **Step:** `100`
- **Display unit:** `ms`
- **Menu:** Driving \> Steering \> ONNX Lane & BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdSmoothingMs -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdSmoothingMs -->
<!-- CARROT:REVIEW reviewed-for="fbbb637458a2aa850365acb0eff1f4fa744b9934ed8dfd981401753968ba6375" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Raising this value smooths BSD confidence more slowly; lowering it responds faster to new results. The release threshold is 15 percentage points below activation, with a floor of zero.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdSmoothingMs -->

<!-- CARROT:SETTING:END OnnxBsdSmoothingMs -->
