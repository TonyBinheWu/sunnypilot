<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_START" param="TeslaManualLaneSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla Manual Lane Lamps

**Menu:** Driving \> Start & Auto \> Engage

---

<!-- CARROT:SETTING:BEGIN TeslaManualLaneSignals -->
<a id="TeslaManualLaneSignals"></a>

## Tesla Manual Lane Lamps

`TeslaManualLaneSignals`

Requires Tesla Automatic Turn Signals and Share Data. At 30 km/h or more, driver torque, sustained boundary approach, repeated ONNX dashed classification and adjacent-lane geometry request lamps only, even without cruise. Solid, unknown or stale results block new requests, never physical stalk operation. No colour or same-direction proof and no steering permission. Default OFF; reboot and closed-course validation required.

<!-- CARROT:AUTO:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:AUTO:SOURCE facts="cef5057e173b03073358bf9bc2f899a61d40886ab8aef27181970f184429f5aa" semantic="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Start & Auto \> Engage
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaManualLaneSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaManualLaneSignals -->
<!-- CARROT:REVIEW reviewed-for="669db437b176b1b2fdb9d4effef75f18f63f9ba24fa2385698d782ce9d784aec" reviewed-at="2026-11-08T01:13:19.682371+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

ON observes sustained driver torque and paired-boundary approach, requesting left/right lamps without cruise; OFF leaves ATC/App lamps unchanged. Both sides require repeated fresh ONNX dashed results, confident adjacent-lane geometry and road-edge clearance at 30 km/h or more. It never writes steering desires.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Requires Tesla Automatic Turn Signals, Share Data, supported vehicle CAN and physical stalk/feedback. Reboot after changing. Visual BSD remains independent. Driver input/hazards, invalid context, lost evidence, retreat, completed crossing or 12 seconds end the observation through the existing cancel/OFF handshake.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Two distinct dashed completion timestamps must span 0.2 seconds and remain at most 0.8 seconds old; the default 400 ms inference interval is unchanged. Completion time is not capture time. Solid/dashed does not prove white/yellow, same-direction traffic or free space. No navigation turn preannouncement, distance add-on or U-turn implementation; no guaranteed detection before tire crossing. Closed-course vehicle acceptance remains required.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaManualLaneSignals -->

<!-- CARROT:SETTING:END TeslaManualLaneSignals -->
