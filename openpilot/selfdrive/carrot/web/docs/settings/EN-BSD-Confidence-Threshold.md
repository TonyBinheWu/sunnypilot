<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_ONNX" param="OnnxBsdThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# BSD Confidence Threshold

**Menu:** Driving \> Steering \> ONNX Lane & BSD

---

<!-- CARROT:SETTING:BEGIN OnnxBsdThreshold -->
<a id="OnnxBsdThreshold"></a>

## BSD Confidence Threshold

`OnnxBsdThreshold`

Minimum confidence required to treat a vehicle in the detection area as a camera blindspot warning.

<!-- CARROT:AUTO:BEGIN OnnxBsdThreshold -->
<!-- CARROT:AUTO:SOURCE facts="3b293b576efc4243e18bee30d125ef9e3e60fe05ca8d3a993e71db3e48365182" semantic="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `94%`
- **Range:** `0%` ~ `100%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Driving \> Steering \> ONNX Lane & BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdThreshold -->
<!-- CARROT:REVIEW reviewed-for="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Raising this value requires more confidence in the blind-spot-threat class; lowering it allows warnings at lower confidence. The distant/rear-vehicle class does not activate the warning.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdThreshold -->

<!-- CARROT:SETTING:END OnnxBsdThreshold -->
