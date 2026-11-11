<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoTurnControlSpeedTurn" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# ATC: Turn Speed(20)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlSpeedTurn -->
<a id="AutoTurnControlSpeedTurn"></a>

## ATC: Turn Speed(20)

`AutoTurnControlSpeedTurn`

(APN)0: not use, Turn Speed

<!-- CARROT:AUTO:BEGIN AutoTurnControlSpeedTurn -->
<!-- CARROT:AUTO:SOURCE facts="b482e655c1400182bfaeea02c8eec3a2535dcfbc7015aa9c7f6bc76f7e4bf54c" semantic="faad48b2a790f2c99af8ac2842c96d8e3a430972367fdf5e0eb2fa6ebfc3f18f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `20km/h`
- **Range:** `0km/h` ~ `100km/h`
- **Step:** `5`
- **Display unit:** `km/h`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlSpeedTurn -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlSpeedTurn -->
<!-- CARROT:REVIEW reviewed-for="faad48b2a790f2c99af8ac2842c96d8e3a430972367fdf5e0eb2fa6ebfc3f18f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

(APN)0: not use, Turn Speed.

- **Higher:** Raises the applicable speed or speed threshold.
- **Lower:** Lowers the speed or threshold.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Test where lane markings are clear and nearby traffic is absent, checking the wait, lane validation, and completion timing after signaling.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0` disables the ATC turn target speed.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoTurnControlSpeedTurn -->

<!-- CARROT:SETTING:END AutoTurnControlSpeedTurn -->
