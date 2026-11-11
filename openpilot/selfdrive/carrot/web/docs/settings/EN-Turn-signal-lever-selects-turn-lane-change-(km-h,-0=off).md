<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="BlinkerLatchedTurn" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Turn-signal lever selects turn / lane change (km/h, 0=off)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN BlinkerLatchedTurn -->
<a id="BlinkerLatchedTurn"></a>

## Turn-signal lever selects turn / lane change (km/h, 0=off)

`BlinkerLatchedTurn`

Hyundai CAN-FD only (0x3C1 lever signal). 0 = off. At or below the set speed a one-touch (half) press, then latching the lever after the lamp has lit, gone dark and lit again, means a left/right turn; a plain latch or a one-touch press means a lane change; no lane change starts while the lever is still in the one-touch position (a latch passes through it for about 0.1 s). Above the set speed any lever input, latched included, is a lane change.

<!-- CARROT:AUTO:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:AUTO:SOURCE facts="ef1bc08ae9b3e2257a4c52f5b334005fde37f205c089035156c9e2261c8ccba5" semantic="76514ada656e4e01d74e337bcc01f3dc8948509aca88bc57278eade000b25502" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0km/h`
- **Range:** `0km/h` ~ `80km/h`
- **Step:** `5`
- **Display unit:** `km/h`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END BlinkerLatchedTurn -->

<!-- CARROT:MANUAL:BEGIN BlinkerLatchedTurn -->
<!-- CARROT:REVIEW reviewed-for="76514ada656e4e01d74e337bcc01f3dc8948509aca88bc57278eade000b25502" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

At or below the selected speed, one-touch followed by two lamp lightings and then latching requests a turn. An ordinary latch or one-touch requests a lane change; raising the value extends the speed range for the turn gesture. Zero preserves the existing classifier.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Requires supported Hyundai CAN-FD lever signals. Above the selected speed, the same gesture requests a lane change.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END BlinkerLatchedTurn -->

<!-- CARROT:SETTING:END BlinkerLatchedTurn -->
