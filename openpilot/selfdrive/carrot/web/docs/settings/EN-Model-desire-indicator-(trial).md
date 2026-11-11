<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="ModelDesireIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Model desire indicator (trial)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN ModelDesireIndicator -->
<a id="ModelDesireIndicator"></a>

## Model desire indicator (trial)

`ModelDesireIndicator`

Indicates repeated dominant model turn/lane-change predictions of at least 50%. Starts with lateral control active, at 10km/h for turns or 30km/h for lane changes. Does not add an automatic steering request. Default OFF; Ioniq 5 PE with Jetson USB2CAN and AutoBlinkerControl 1 or 2. Physical lamp and road validation remain separate. At 30 km/h or above, the two nearest model forecasts can also trigger an indication when both predict the same lane change with at least 65% probability and both measured lane boundaries show the vehicle approaching that side. A forecast alone does not light the indicator or request steering. After forecast-based initiation, widening lane lines at a fork do not end the hold while the model and measured motion still indicate the same direction. Fading or opposite intent ends the fork hold; cruise CANCEL releases it immediately.

<!-- CARROT:AUTO:BEGIN ModelDesireIndicator -->
<!-- CARROT:AUTO:SOURCE facts="18bb3c189f1c687133c41c52144ffd4543a91a6c9b73f9877fc09a81159a9245" semantic="85643599439e3e55d38ab927bf13b2d2b17ffa165c1e3dd5f7b7d003daaf5a6d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelDesireIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelDesireIndicator -->
<!-- CARROT:REVIEW reviewed-for="85643599439e3e55d38ab927bf13b2d2b17ffa165c1e3dd5f7b7d003daaf5a6d" reviewed-at="2026-11-10T10:51:22.871833+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Indicates repeated dominant model turn or lane-change predictions while lateral control is active. It neither changes existing ATC admission nor adds a steering request.

Another same-direction origin shares the continuing signal without another tap. Physical illumination and detection rates require separate verification.
Manual/model indication distinguishes its short one-touch echo only with matching request time, direction and stalk counters. Opposite input, a latched lever or receiver-detected driver intervention cancels. Lamp feedback preceding the completed-send response is remembered briefly; holding still requires the matching response. Same-direction physical input during the brief transmission interval cannot be uniquely distinguished from these fields alone.

At 30 km/h or above, the two nearest model forecasts can also trigger an indication when both predict the same lane change with at least 65% probability and both measured lane boundaries show the vehicle approaching that side. A forecast alone does not light the indicator or request steering.

After forecast-based initiation, widening lane lines at a fork do not end the hold while the model and measured motion still indicate the same direction. Fading or opposite intent ends the fork hold; cruise CANCEL releases it immediately.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelDesireIndicator -->

<!-- CARROT:SETTING:END ModelDesireIndicator -->
