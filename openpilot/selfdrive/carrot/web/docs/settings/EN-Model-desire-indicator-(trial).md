<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="ModelDesireIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Model desire indicator (trial)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN ModelDesireIndicator -->
<a id="ModelDesireIndicator"></a>

## Model desire indicator (trial)

`ModelDesireIndicator`

Indicates repeated dominant model turn/lane-change predictions of at least 50%. Starts with lateral control active, at 10km/h for turns or 30km/h for lane changes. Does not add an automatic steering request. Default OFF; Ioniq 5 PE with Jetson USB2CAN and AutoBlinkerControl 1 or 2. Physical lamp and road validation remain separate. At 30 km/h or above, the two nearest model forecasts can also trigger an indication when both predict the same lane change with at least 65% probability and both measured lane boundaries show the vehicle approaching that side. A forecast alone does not light the indicator or request steering. After forecast-based initiation, widening lane lines at a fork do not end the hold while the model and measured motion still indicate the same direction. Fading or opposite intent ends the fork hold; cruise CANCEL releases it immediately. Model-turn indication also requires at least 15 degrees of same-direction steering and 3 degrees/s of measured rotation. While moving, a turn probability below 30% and wheel return within ±10 degrees for 0.4s end the hold.

<!-- CARROT:AUTO:BEGIN ModelDesireIndicator -->
<!-- CARROT:AUTO:SOURCE facts="435c8c3010f84bb7fae300a9b42fd791e5abe6b95709ee402c72177c230f2e42" semantic="d73f84bcf6ba7064705bfb722d8a81eb4a2d19fa2936d3d3e21fe478a59c63b5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ModelDesireIndicator -->

<!-- CARROT:MANUAL:BEGIN ModelDesireIndicator -->
<!-- CARROT:REVIEW reviewed-for="d73f84bcf6ba7064705bfb722d8a81eb4a2d19fa2936d3d3e21fe478a59c63b5" reviewed-at="2026-11-14T02:05:14Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Indicates repeated dominant model turn or lane-change predictions while lateral control is active. It neither changes existing ATC admission nor adds a steering request.

Another same-direction origin shares the continuing signal without another tap. Physical illumination and detection rates require separate verification.
Manual/model indication distinguishes its short one-touch echo only with matching request time, direction and stalk counters. Opposite input, a latched lever or receiver-detected driver intervention cancels. Lamp feedback preceding the completed-send response is remembered briefly; holding still requires the matching response. Same-direction physical input during the brief transmission interval cannot be uniquely distinguished from these fields alone.

At 30 km/h or above, the two nearest model forecasts can also trigger an indication when both predict the same lane change with at least 65% probability and both measured lane boundaries show the vehicle approaching that side. A forecast alone does not light the indicator or request steering.

After forecast-based initiation, widening lane lines at a fork do not end the hold while the model and measured motion still indicate the same direction. Fading or opposite intent ends the fork hold; cruise CANCEL releases it immediately.
Model-turn initiation additionally requires at least 15 degrees of same-direction wheel angle and fresh measured rotation of at least 3 degrees/s. While moving, a turn probability below 30% and wheel return within ±10 degrees for 0.4 seconds can end the hold before the old 30-degree peak has been reached.

With B1 release 5, a confirmed own-tap echo can remain accepted through dark flash intervals. Neutral feedback after the tap closes that allowance; a later lever report cancels ownership. Opposite lamps, raw driver input, invalid CAN and expired leases still cancel. Software replay does not establish physical hold or cancellation performance.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ModelDesireIndicator -->

<!-- CARROT:SETTING:END ModelDesireIndicator -->
