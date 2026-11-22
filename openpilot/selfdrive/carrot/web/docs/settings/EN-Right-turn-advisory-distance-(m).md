<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="AutoTurnControlRightLaneChange" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Right-turn advisory distance (m)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN AutoTurnControlRightLaneChange -->
<a id="AutoTurnControlRightLaneChange"></a>

## Right-turn advisory distance (m)

`AutoTurnControlRightLaneChange`

Distance for a right-turn or right-fork advisory on supported indicator adapters. Set 0 m to turn it off or up to 500 m for an earlier check. Requires ATC mode 1 or 2 and automatic indicator mode 2. The driver requests the lane change.

<!-- CARROT:AUTO:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:AUTO:SOURCE facts="691595ec59c5d8825c0476b84365324d83997a62f9ba60b2650189f2afee31f0" semantic="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `500`
- **Step:** `50`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoTurnControlRightLaneChange -->

<!-- CARROT:MANUAL:BEGIN AutoTurnControlRightLaneChange -->
<!-- CARROT:REVIEW reviewed-for="517c131dc727f1d4463382c4d3c83de1677184ce198f650ff90d5937e35160e1" reviewed-at="2026-11-22T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Distance for a right-turn or right-fork advisory on supported indicator adapters. Set 0 m to turn it off or up to 500 m for an earlier check. Requires ATC mode 1 or 2 and automatic indicator mode 2. The driver requests the lane change.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END AutoTurnControlRightLaneChange -->

<!-- CARROT:SETTING:END AutoTurnControlRightLaneChange -->
