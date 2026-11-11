<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_TRAFFIC" param="SignalAssistMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Signal Assistance Mode (Trial)

**Menu:** Driving \> Speed & Decel \> Traffic Light

---

<!-- CARROT:SETTING:BEGIN SignalAssistMode -->
<a id="SignalAssistMode"></a>

## Signal Assistance Mode (Trial)

`SignalAssistMode`

0: Observer, display and assistance off. 1: Show recognition throughout driving, with alerts and a stopped-red departure veto. 2: Mode 1 plus moving preparation toward -0.5m/s² with qualified red evidence when no lead is within 50m. Either tracked lead at or within 50m cancels extra preparation; normal lead following remains. Once stopped, behavior is identical to mode 1. The stopped-red veto retains its stop memory only up to 5km/h and clears it above that speed. Preparation does not command a full stop. Night evidence requires two red lamps and road-direction support. Missing red or conflicting green cancels preparation. Display is independent of control activity; previous results are dim for at most two seconds, then unknown. Experimental and separate from the driving model; false and missed detections remain possible.

<!-- CARROT:AUTO:BEGIN SignalAssistMode -->
<!-- CARROT:AUTO:SOURCE facts="b749580573f91aa2200dbabc1cc5ae47391c700639e105a7ba001acc2536e1f4" semantic="ba8119151eab7971db5323d2e70e29e83140178360a67bae13fb690b0084d730" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Speed & Decel \> Traffic Light
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SignalAssistMode -->

<!-- CARROT:MANUAL:BEGIN SignalAssistMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The stopped-red veto keeps its memory during stopping and creeping, then clears it above 5km/h. Losing a lead after departure cannot reactivate that old stop; normal model and lead control and explicit driver holds remain active.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END SignalAssistMode -->

<!-- CARROT:SETTING:END SignalAssistMode -->
