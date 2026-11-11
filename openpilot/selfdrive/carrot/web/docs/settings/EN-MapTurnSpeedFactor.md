<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CURVE" param="MapTurnSpeedFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# MapTurnSpeedFactor

**Menu:** Driving \> Speed & Decel \> Curve & Turn

---

<!-- CARROT:SETTING:BEGIN MapTurnSpeedFactor -->
<a id="MapTurnSpeedFactor"></a>

## MapTurnSpeedFactor

`MapTurnSpeedFactor`

The smaller the value, the more the speed will decrease along the route.

<!-- CARROT:AUTO:BEGIN MapTurnSpeedFactor -->
<!-- CARROT:AUTO:SOURCE facts="7a203c4c5111a0cf21a1abc9de9aa55345db366756b6ba7013fd934b28c17994" semantic="70911cfe4337b36f9b1812b46852781a33788b52e9f58c2bf5e64debf1f9fa80" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100%`
- **Range:** `50%` ~ `300%`
- **Step:** `10`
- **Display unit:** `%`
- **Menu:** Driving \> Speed & Decel \> Curve & Turn
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MapTurnSpeedFactor -->

<!-- CARROT:MANUAL:BEGIN MapTurnSpeedFactor -->
<!-- CARROT:REVIEW reviewed-for="70911cfe4337b36f9b1812b46852781a33788b52e9f58c2bf5e64debf1f9fa80" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The smaller the value, the more the speed will decrease along the route.

- **Higher:** Reduces route-turn deceleration.
- **Lower:** Increases route-based deceleration.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Adjust one item at a time on the same curve and route-guidance condition, comparing the target before entry and the speed through the curve.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> This applies only when route-based turn information is connected.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MapTurnSpeedFactor -->

<!-- CARROT:SETTING:END MapTurnSpeedFactor -->
