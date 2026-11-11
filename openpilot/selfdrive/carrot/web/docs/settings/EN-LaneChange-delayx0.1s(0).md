<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="LaneChangeDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LaneChange delayx0.1s(0)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN LaneChangeDelay -->
<a id="LaneChangeDelay"></a>

## LaneChange delayx0.1s(0)

`LaneChangeDelay`

Changes lanes after the set time once the turn signal is activated

<!-- CARROT:AUTO:BEGIN LaneChangeDelay -->
<!-- CARROT:AUTO:SOURCE facts="a82528b55d319d511c85e0a663115ceaad2792b2e56b0786f526220e12f63c0d" semantic="6740c9942977f73420ed5c963b1d5773b4d958e0c8fb4bb8e03d397a45348792" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `100`
- **Step:** `10`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeDelay -->

<!-- CARROT:MANUAL:BEGIN LaneChangeDelay -->
<!-- CARROT:REVIEW reviewed-for="6740c9942977f73420ed5c963b1d5773b4d958e0c8fb4bb8e03d397a45348792" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Changes lanes after the set time once the turn signal is activated.

- **Higher:** Increases the applicable time or delay.
- **Lower:** Decreases the time or delay.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Test where lane markings are clear and nearby traffic is absent, checking the wait, lane validation, and completion timing after signaling.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

This setting changes the wait before entry, not the speed of a lane change already in progress. See [Understanding Lane Changes](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md).
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneChangeDelay -->

<!-- CARROT:SETTING:END LaneChangeDelay -->
