<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="LaneChangeNeedTorque" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LaneChange use steering torque

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN LaneChangeNeedTorque -->
<a id="LaneChangeNeedTorque"></a>

## LaneChange use steering torque

`LaneChangeNeedTorque`

0:immediate, 1: need torque(nudge), -1: auto lane change off

<!-- CARROT:AUTO:BEGIN LaneChangeNeedTorque -->
<!-- CARROT:AUTO:SOURCE facts="0bd744c26fc69aad74106daeb3ca8b4b15cbb65c8b79c9178a358976163ef05b" semantic="70cb75233be32678e1cf5e9957be1e809887dca4e08053751f65ac6a2f29c189" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `-1` ~ `1`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeNeedTorque -->

<!-- CARROT:MANUAL:BEGIN LaneChangeNeedTorque -->
<!-- CARROT:REVIEW reviewed-for="70cb75233be32678e1cf5e9957be1e809887dca4e08053751f65ac6a2f29c189" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — immediate
- `1` — need torque(nudge)
- `-1` — auto lane change off
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Test where lane markings are clear and nearby traffic is absent, checking the wait, lane validation, and completion timing after signaling.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

See [Understanding Lane Changes](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md) for who determines the path and the driver's safety responsibility.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeNeedTorque -->

<!-- CARROT:SETTING:END LaneChangeNeedTorque -->
