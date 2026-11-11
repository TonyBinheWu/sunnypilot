<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="ModelPathIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Model path indicator (trial)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN ModelPathIndicator -->
<a id="ModelPathIndicator"></a>

## Model path indicator (trial)

`ModelPathIndicator`

At 30km/h or above, indicates a model path crossing the curved boundary within 1–3 seconds while commanded curvature agrees. Requires target-line confidence of at least 10%, continuous geometry and repeated observations. Applies left centre-line and right road-edge exclusions; adds no steering request. Default OFF; Ioniq 5 PE with Jetson USB2CAN and AutoBlinkerControl 1 or 2. Physical lamp and road validation remain separate.

<!-- CARROT:AUTO:BEGIN ModelPathIndicator -->
<!-- CARROT:AUTO:SOURCE facts="ce85ef845db3e48ee8712306c8439177094a035843e71158332be11d7df9b7cf" semantic="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelPathIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelPathIndicator -->
<!-- CARROT:REVIEW reviewed-for="09c4851f68312e9070186bb23698703b51d5b7dce50dbeca5e9cb4cf5626b6c8" reviewed-at="2026-11-01T04:38:46.046271+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Compares the model path with curved boundaries at identical forward positions to detect sustained crossing. Requires at least 10% target-line confidence, continuous geometry, repeated observations and agreeing control relative to road curvature.

Boundary relabeling alone does not create a request; generated signals cannot request steering. Wide shoulders and intersections remain limitations of boundary estimation.
Manual/model indication distinguishes its short one-touch echo only with matching request time, direction and stalk counters. Opposite input, a latched lever or receiver-detected driver intervention cancels. Lamp feedback preceding the completed-send response is remembered briefly; holding still requires the matching response. Same-direction physical input during the brief transmission interval cannot be uniquely distinguished from these fields alone.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelPathIndicator -->

<!-- CARROT:SETTING:END ModelPathIndicator -->
