<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_START" param="TeslaModelDesireSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla Model Desire Lamps

**Menu:** Driving \> Start & Auto \> Engage

---

<!-- CARROT:SETTING:BEGIN TeslaModelDesireSignals -->
<a id="TeslaModelDesireSignals"></a>

## Tesla Model Desire Lamps

`TeslaModelDesireSignals`

Independent default-OFF lane-change prediction lamps: requires Tesla Automatic Turn Signals, Share Data, active lateral control, 30 km/h, repeated model lane-change probability and fresh ONNX dashed/adjacent-lane evidence. May light before an actual maneuver or falsely. Does not use navigation turn announcements, predict U-turns or authorize steering. Reboot and closed-course validation required.

<!-- CARROT:AUTO:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:AUTO:SOURCE facts="944d2b2cbfc8a225841f21077edd1c752fd6aa41c1a8f26deb5a69be4f8082d8" semantic="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Start & Auto \> Engage
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelDesireSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelDesireSignals -->
<!-- CARROT:REVIEW reviewed-for="bca04977c235f3a14fba9b7ea53e0b0d380d401a15291409e8f45d1bfb0bedc7" reviewed-at="2026-11-08T01:13:19.707928+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

ON requests lamps for a dominant lane-change probability repeated over at least four unique model frames and 0.2 seconds; OFF does not use this prediction. Requires active lateral control, 30 km/h and the same fresh ONNX dashed/adjacent-lane evidence as manual lamp observations. It never creates a steering request.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Requires Tesla Automatic Turn Signals, Share Data and supported vehicle CAN/stalk/feedback; reboot after changing. Independent of manual and path options. Existing ATC/App intent takes priority. Context/evidence loss, completion, retreat or 12 seconds cancels; continuous predictions cannot replay a consumed observation without neutral prediction and dark-lamp rearming.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

May light early or falsely. Two distinct dashed updates span 0.2 seconds, completion age is at most 0.8 seconds, not total capture age; the 400 ms default inference interval is unchanged. No colour/same-direction/free-space proof, navigation turn preannouncement, turn prediction or U-turn logic. Desktop tests do not establish physical acceptance.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelDesireSignals -->

<!-- CARROT:SETTING:END TeslaModelDesireSignals -->
