<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="ManualTurnIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Manual turn indicator (trial)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN ManualTurnIndicator -->
<a id="ManualTurnIndicator"></a>

## Manual turn indicator (trial)

`ManualTurnIndicator`

Detects driver turns using steering torque, wheel movement and measured vehicle rotation. Operates independently of ATC, including intersections with faint lane markings. Starts at 5–60km/h after 0.15s same-direction driver torque, at least 42 degrees steering with a 22-degree increase and consistent vehicle rotation. Ends after wheel return within ±15 degrees and settled rotation, opposite driver steering, or 30 seconds. Default OFF. Requires Ioniq 5 PE, a supported indicator adapter and AutoBlinkerControl 1 or 2. Parking-aisle turns can also trigger. Curves and evasive maneuvers can cause false indications. Physical lamp validation remains pending.

<!-- CARROT:AUTO:BEGIN ManualTurnIndicator -->
<!-- CARROT:AUTO:SOURCE facts="ee534ae5553734f36e35112db8a494ecd7969994b63a4b613a0cf0288f9e0f1a" semantic="376bcf8235f7ad9de6c1ed48484745355356b0c0edbb66be12b5637052655754" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualTurnIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualTurnIndicator -->
<!-- CARROT:REVIEW reviewed-for="376bcf8235f7ad9de6c1ed48484745355356b0c0edbb66be12b5637052655754" reviewed-at="2026-11-08T12:45:07+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Combines same-direction driver torque, increasing wheel angle and fresh measured vehicle rotation to indicate a turn. Works independently of ATC and lateral-control activation, with lamp feedback isolated from automatic steering requests.

Wheel return and settled rotation complete the request. Opposite driver steering, invalid inputs or disabling the setting end it.
A new manual turn requires two seconds since the previous indication last renewed its hold and one continuous second with both lamps off. These intervals run concurrently.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

After Git Pull, restart comma and enable this option. Requires Ioniq 5 PE with a supported indicator adapter and AutoBlinkerControl 1 or 2.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Parking aisles, ramps and parking entry can also trigger. Unmarked bends and evasive movements can produce false indications. Physical lamp validation remains pending.

[Detailed conditions](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md)
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END ManualTurnIndicator -->

<!-- CARROT:SETTING:END ManualTurnIndicator -->
