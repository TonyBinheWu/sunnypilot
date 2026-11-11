<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="LaneChangeBsd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LaneChange BSD

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN LaneChangeBsd -->
<a id="LaneChangeBsd"></a>

## LaneChange BSD

`LaneChangeBsd`

0:BSD detect(allow steer torque), 1: block steer torque, -1: ignore BSD

<!-- CARROT:AUTO:BEGIN LaneChangeBsd -->
<!-- CARROT:AUTO:SOURCE facts="e4ef47cf967046f0cbf5cd9565179628603762c1f787e7a4602db04da0015e57" semantic="04954a5af52833d5de668494cc66d168955efdddb321270af7866ff7bd295569" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `-1` ~ `1`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeBsd -->

<!-- CARROT:MANUAL:BEGIN LaneChangeBsd -->
<!-- CARROT:REVIEW reviewed-for="04954a5af52833d5de668494cc66d168955efdddb321270af7866ff7bd295569" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — BSD detect(allow steer torque)
- `1` — block steer torque
- `-1` — ignore BSD
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Test where lane markings are clear and nearby traffic is absent, checking the wait, lane validation, and completion timing after signaling.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

BSD does not replace the driver's blind-spot and rear-traffic checks. See [Understanding Lane Changes](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md).
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeBsd -->

<!-- CARROT:SETTING:END LaneChangeBsd -->
