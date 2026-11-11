<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoTurnControlTurnEnd" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: Speed Ctrl left Time(3)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlTurnEnd -->
<a id="AutoTurnControlTurnEnd"></a>

## ATC: Speed Ctrl left Time(3)

`AutoTurnControlTurnEnd`

(APN) NOO Completion Time Distance (Speed × Time)

<!-- CARROT:AUTO:BEGIN AutoTurnControlTurnEnd -->
<!-- CARROT:AUTO:SOURCE facts="a78ad4883ebc5f7a9755ca5921da026df3f7e3e8ce4752596e9fa857e7de3f3c" semantic="55ebb6f698365577e35dd91320b04f3f559583fa75f0b6bffd5f11af27bea89d" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `6`
- **Range:** `0` ~ `30`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlTurnEnd -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlTurnEnd -->
<!-- CARROT:REVIEW reviewed-for="55ebb6f698365577e35dd91320b04f3f559583fa75f0b6bffd5f11af27bea89d" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(APN) NOO Completion Time Distance (Speed × Time).

- **Higher:** Increases the applicable time or delay.
- **Lower:** Decreases the time or delay.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Test where lane markings are clear and nearby traffic is absent, checking the wait, lane validation, and completion timing after signaling.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoTurnControlTurnEnd -->

<!-- CARROT:SETTING:END AutoTurnControlTurnEnd -->
