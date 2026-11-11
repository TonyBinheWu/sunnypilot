<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_START" param="TeslaModelPathSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla Model Path Lamps

**Menu:** Driving \> Start & Auto \> Engage

---

<!-- CARROT:SETTING:BEGIN TeslaModelPathSignals -->
<a id="TeslaModelPathSignals"></a>

## Tesla Model Path Lamps

`TeslaModelPathSignals`

Independent default-OFF path prediction lamps: requires Tesla Automatic Turn Signals, Share Data, active lateral control, 30 km/h, repeated predicted boundary crossing relative to lane curvature and fresh ONNX dashed/adjacent-lane evidence. May light early or falsely; no navigation turn preannouncement, U-turn logic or steering permission. Reboot and closed-course validation required.

<!-- CARROT:AUTO:BEGIN TeslaModelPathSignals -->
<!-- CARROT:AUTO:SOURCE facts="24f31c2a98eee2978e77ab62a55cde4cd33f2e8f9440c78a723348351b72b463" semantic="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Start & Auto \> Engage
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaModelPathSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaModelPathSignals -->
<!-- CARROT:REVIEW reviewed-for="edf04a247afa9d6aaf6f0a28c3a2a9441df5e3bfed9758d06e290ced61ea05b0" reviewed-at="2026-11-08T01:13:19.729984+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

ON requests lamps for repeated model-path crossing relative to curved lane boundaries; OFF does not use this prediction. At least four unique frames over 0.2 seconds, active lateral control, 30 km/h and fresh ONNX dashed/adjacent-lane evidence are required. No model or steering command is changed.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Requires Tesla Automatic Turn Signals, Share Data and supported CAN/stalk/feedback; reboot after changing. Independent of manual and desire options. ATC/App takes priority. Evidence/context loss, return, completion or 12 seconds cancels through the existing executor; neutral prediction and dark lamps are required before rearming.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Predictions may light early or falsely, not detect every crossing. Two distinct dashed updates span 0.2 seconds and completion age is at most 0.8 seconds, not capture age; the default 400 ms interval stays unchanged. Dashed is not colour, same-direction or free-space proof. No navigation turn preannouncement, turn prediction or U-turn logic; physical closed-course acceptance remains unverified.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaModelPathSignals -->

<!-- CARROT:SETTING:END TeslaModelPathSignals -->
