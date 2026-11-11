<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_LIMIT" param="AutoSpeedUptoRoadSpeedLimit" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# AutoSpeedUpx:(100)%

**Menu:** Driving \> Speed & Decel \> Speed Limit

---

<!-- CARROT:SETTING:BEGIN AutoSpeedUptoRoadSpeedLimit -->
<a id="AutoSpeedUptoRoadSpeedLimit"></a>

## AutoSpeedUpx:(100)%

`AutoSpeedUptoRoadSpeedLimit`

Automatically increases speed on lead car, up to (road speed x ratio)

<!-- CARROT:AUTO:BEGIN AutoSpeedUptoRoadSpeedLimit -->
<!-- CARROT:AUTO:SOURCE facts="1e333cd54360f0280c641d0e346fd07d02ab19c9271b97fd60db50168998ce7a" semantic="c05370fd34043aeafdf056f429b15308e3f72dadec462c9d4d3b6c332b0d48d1" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `0%` ~ `200%`
- **Step:** `10`
- **Display unit:** `%`
- **Menu:** Driving \> Speed & Decel \> Speed Limit
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoSpeedUptoRoadSpeedLimit -->

<!-- CARROT:MANUAL:BEGIN AutoSpeedUptoRoadSpeedLimit -->
<!-- CARROT:REVIEW reviewed-for="c05370fd34043aeafdf056f429b15308e3f72dadec462c9d4d3b6c332b0d48d1" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Disables lead-based automatic set-speed increase.
- **Positive:** When a lead within 60 m is near the current set speed, raises the set speed in 5 km/h steps up to the road speed limit multiplied by this ratio.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the new target speed and transition timing on the same section where the road speed limit changes.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoSpeedUptoRoadSpeedLimit -->

<!-- CARROT:SETTING:END AutoSpeedUptoRoadSpeedLimit -->
