<!-- CARROT:GENERATED schema="1" locale="en" group="TESLA_FEATURES" param="TeslaAutoTurnSignals" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Tesla Automatic Turn Signals

**Menu:** Driving \> Tesla \> Tesla Features

---

<!-- CARROT:SETTING:BEGIN TeslaAutoTurnSignals -->
<a id="TeslaAutoTurnSignals"></a>

## Tesla Automatic Turn Signals

`TeslaAutoTurnSignals`

Model 3/Y with vehicle CAN and a physical stalk: no turn pre-signalling; measured heading/wheel return complete turns. Only confirmed turns may wait at standstill under fresh permission. Lane-change preparation lamps remain. Driver priority and steering/departure permissions are unchanged. Default OFF; reboot required. Validate in a closed course before road use.

<!-- CARROT:AUTO:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:AUTO:SOURCE facts="9af96d5636abbc71788d451dcc318d4cbcce49611677b9e2541800021b38cc11" semantic="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Tesla \> Tesla Features
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TeslaAutoTurnSignals -->

<!-- CARROT:MANUAL:BEGIN TeslaAutoTurnSignals -->
<!-- CARROT:REVIEW reviewed-for="8b6946fdb18666d41bbb517905b3d386b2941ffcbbf16b84ab7bf6f7eb3920a6" reviewed-at="2026-11-08T01:13:19.636591+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Turn lamps start with turn desire, not navigation preparation or distance alone. Lane changes retain preparation-stage lamp confirmation. Completion requires fresh measured heading (20 degrees), selected steering above 30 degrees and wheel return within 15 degrees while moving at least 1 km/h. Only TX/lamp-confirmed turns may wait at true standstill under fresh lateral permission and healthy pose, never new requests or lane changes. A following cue waits for completion and current turn desire (three-second queue); same-side handoff retains the ID. The 60-second limit, new idle template and TX echo per repeat, manual priority and cancel/OFF handshake remain. Missing feedback ends the session; unconfirmed cancellation blocks this onroad cycle. Desktop tests do not prove sustained physical lamps.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Default OFF; reboot after changing. Requires supported Model 3/Y, CAN1 extension detection shared with the speed wheel (`0x3DF`), fresh physical stalk input and matching Panda firmware. CAN1 stalk input is preferred once observed; stale or conflicting input blocks output. Lamp-specific templates and UI/physical feedback are still required. App requests last through the existing maneuver. `blocked:*` and `waiting:*` diagnostics identify blockers; they are not new on-screen alerts. It does not grant steering or departure permission. Validate both directions and failure/manual takeover on the exact vehicle in a closed course before road use. CAN or device power loss cannot guarantee lamp cancellation.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Execution: `openpilot/selfdrive/car/tesla_turn_signals.py`. Intent: `openpilot/selfdrive/controls/lib/desire_helper.py`. Safety: `opendbc_repo/opendbc/safety/safety/safety_tesla_turn_signals.h`. See the Tesla user guide for diagnostics and limitations.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TeslaAutoTurnSignals -->

<!-- CARROT:SETTING:END TeslaAutoTurnSignals -->
