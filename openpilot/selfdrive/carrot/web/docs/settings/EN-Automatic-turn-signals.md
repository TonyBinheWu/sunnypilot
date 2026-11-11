<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Automatic turn signals

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoBlinkerControl -->
<a id="AutoBlinkerControl"></a>

## Automatic turn signals

`AutoBlinkerControl`

0: Off (Bluetooth one-touch remains). 1: Hold Bluetooth signals started at or below 5 km/h until the turn completes; indicate from the ATC audioTurn cue through intersection stops until the vehicle turns and the steering returns near center. 2: Also indicate during actual ATC lane changes, excluding waiting. Same direction cancels a hold; opposite direction switches. Stock lever has priority. Requires a supported Jetson USB-CAN/B1 vehicle. ATC permits one retry after confirmed transmission without illumination. A confirmed straight passage using a valid TBT point and raw vehicle GPS cancels the indication. Uncertain location disables this location-based cancellation. TBT turns track the audioTurn distance and wheel-speed travel through 30m past the turn. After selected-side steering exceeds 30 degrees and heading rotates at least 20 degrees, wheel return within ±15 degrees at 1km/h or above immediately ends the hold. Pre-turn traffic-light waits remain held. A fresh next-turn cue is handed over at completion; after steering at least 30 degrees toward the turn, driver torque carrying the wheel across zero into the opposite direction cancels it. A TBT hold with confirmed transmission and illumination continues through a receiver driver\_override status. Immediate OEM lamp extinction is not guaranteed. Cruise CANCEL stops automatic indicator requests and releases an automatic hold. Parking maneuvers no longer trigger an indication until SET/RES or +/− clears the cruise cancel state. The stock lever and explicit Bluetooth indicator buttons remain available.

<!-- CARROT:AUTO:BEGIN AutoBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="db4cd3bd53a8f3018322d460d821b9b9976a87ebd16b6677108fb996a31f9bd1" semantic="edd05659292aebc71be712906d3faaadf71c30551e5a372287abb2bf65bd60ca" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN AutoBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="edd05659292aebc71be712906d3faaadf71c30551e5a372287abb2bf65bd60ca" reviewed-at="2026-11-10T10:39:14.890627+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Manages physical BT/ATC indicator requests and holds on supported vehicles.

After confirmed turn entry, wheel return within ±15 degrees while moving completes the TBT turn. Travel beyond the turn point also supplies completion criteria. After steering at least 30 degrees toward the turn, opposite driver torque crossing zero into the opposite direction cancels it.

A TBT hold with confirmed transmission and illumination continues through receiver driver_override until completion. A missing initial transmission acknowledgement prevents hold activation. A fresh next-turn cue is handed over at completion.

Cruise CANCEL stops automatic indicator requests and releases an automatic hold. Parking maneuvers no longer trigger an indication until SET/RES or +/− clears the cruise cancel state. The stock lever and explicit Bluetooth indicator buttons remain available.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoBlinkerControl -->

<!-- CARROT:SETTING:END AutoBlinkerControl -->
