<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Right lane-change distance before a turn (m)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## Right lane-change distance before a turn (m)

`AutoTurnControlRightLaneChange`

Zero metres disables the add-on. Set the distance to begin checking conditions. A value of 250m retains the former range, and 300–400m can also be selected. The former ON setting migrates to 250m at startup. Adds to existing ATC modes 1 and 2. At 10km/h or above and within the configured distance of a TBT right turn or right fork, requests the right indicator until the turn starts. Requires the Ioniq 5 PE USB2CAN setup, AutoBlinkerControl=2 and LaneChangeNeedTorque=0. Rear admission uses fresh OEM BSD warnings only, without corner distances. Every detected right-lane front target must be at least 5m away now and after a three-second constant-relative-speed projection. Radar errors or stale input block initiation. Steering before a request resets confirmation; driver intervention after a request cancels it. Signals started below 30km/h remain indication-only until they end; only starts at or above 30km/h enter ordinary lane-change handling. Requires at least 2.5m beyond the right boundary to the road edge.

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="69f345289c078e233e7e0546de33c7004169918a0234a9843b4b9667bcc7e3ca" semantic="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `500`
- **Step:** `50`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="3008498ad9b26c4e6721da72acaa56057939a66d7d15c51954adbc9bb64b1584" reviewed-at="2026-11-02T22:15:29.514979+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Zero metres disables the add-on. Higher values check conditions farther before a right turn or fork. A value of 250m uses the former range, and the former ON setting migrates to 250m at restart.

At 10km/h or above, checks the right lane/edge, valid BSD and current/projected three-second front gaps. Signals started below 30km/h remain indication-only, while starts at or above 30km/h enter ordinary lane-change handling.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
