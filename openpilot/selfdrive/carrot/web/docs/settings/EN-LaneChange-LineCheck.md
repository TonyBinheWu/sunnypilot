<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="LaneLineCheck" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# LaneChange LineCheck

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN LaneLineCheck -->
<a id="LaneLineCheck"></a>

## LaneChange LineCheck

`LaneLineCheck`

0: Color+Type(block yellow), 1: Type only, 2: Type+torque override solid

<!-- CARROT:AUTO:BEGIN LaneLineCheck -->
<!-- CARROT:AUTO:SOURCE facts="73b060388730d74547d0ae973a86e2199e47e66bd0d6ebda60ef7af49ac17d43" semantic="5977a88be710cace4de2e0c770c5dc27e274c2c55f3693f68730b76f98956e5e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneLineCheck -->

<!-- CARROT:MANUAL:BEGIN LaneLineCheck -->
<!-- CARROT:REVIEW reviewed-for="5977a88be710cace4de2e0c770c5dc27e274c2c55f3693f68730b76f98956e5e" reviewed-at="2026-08-22T10:36:15+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Color+Type(block yellow)
- `1` — Type only
- `2` — Type+torque override solid
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Test where lane markings are clear and nearby traffic is absent, checking the wait, lane validation, and completion timing after signaling.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

The camera or vehicle can misclassify markings, and a solid-line override does not make the crossing safe or legal. See [Understanding Lane Changes](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/lane-change.md).
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LaneLineCheck -->

<!-- CARROT:SETTING:END LaneLineCheck -->
