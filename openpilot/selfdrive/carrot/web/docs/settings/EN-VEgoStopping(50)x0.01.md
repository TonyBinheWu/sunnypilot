<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_STOPGO" param="VEgoStopping" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# VEgoStopping(50)x0.01

**Menu:** Driving \> Cruise & Gap \> Stop & Resume

---

<!-- CARROT:SETTING:BEGIN VEgoStopping -->
<a id="VEgoStopping"></a>

## VEgoStopping(50)x0.01

`VEgoStopping`

Uses planned speeds to determine stop entry and departure. Lower values delay stop recognition and may release stop state sooner on departure. The minimum is 10 (0.10 m/s); previously stored values below 10 are automatically raised to 10.

<!-- CARROT:AUTO:BEGIN VEgoStopping -->
<!-- CARROT:AUTO:SOURCE facts="84d49c554660c2bbb1f43b0318ce727f754becb2d68aa27630eeeccaea4e2af4" semantic="887184b01d8bb7422533a0039715941602b954e65f56f045b2a9a34d9b135001" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `50`
- **Range:** `10` ~ `100`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Stop & Resume
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VEgoStopping -->

<!-- CARROT:MANUAL:BEGIN VEgoStopping -->
<!-- CARROT:REVIEW reviewed-for="887184b01d8bb7422533a0039715941602b954e65f56f045b2a9a34d9b135001" reviewed-at="2026-09-27T06:35:25+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The planner requests stopping when target speeds at the control-delay horizon and one second later are both below the threshold. No additional CANFD early-stop check applies.

**Raise it:** can recognize stopping earlier and delay departure.

**Lower it:** can recognize stopping later and advance departure.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time under comparable lead-vehicle stop and departure conditions; check the final stopping position and departure response. Previously stored values below the current minimum are raised at startup. If a lower value is written during driving, control applies the minimum immediately and repairs storage.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

This is a speed threshold; stopping acceleration follows StoppingAccel. CANFD retry checks sustained speed rebound or loss of deceleration after stop control begins. It does not start while shouldStop is still false. See the [stop and resume guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md#stop-resume).
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END VEgoStopping -->

<!-- CARROT:SETTING:END VEgoStopping -->
