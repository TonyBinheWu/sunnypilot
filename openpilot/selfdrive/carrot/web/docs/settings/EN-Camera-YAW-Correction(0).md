<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_CENTER" param="CameraYawTrimDeg" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Camera YAW Correction(0)

**Menu:** Driving \> Steering \> Centering

---

<!-- CARROT:SETTING:BEGIN CameraYawTrimDeg -->
<a id="CameraYawTrimDeg"></a>

## Camera YAW Correction(0)

`CameraYawTrimDeg`

Fine tunes camera yaw alignment.(+: right)

<!-- CARROT:AUTO:BEGIN CameraYawTrimDeg -->
<!-- CARROT:AUTO:SOURCE facts="398077f5299411ba6758f76364fe393322a8b86bfdc56210a7df9998c87bc0a2" semantic="290906bf88c0f6a12d995faeea4c0ab18dad803aefe18bf89e349b3a45474f4a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `-200` ~ `200`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Centering
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CameraYawTrimDeg -->

<!-- CARROT:MANUAL:BEGIN CameraYawTrimDeg -->
<!-- CARROT:REVIEW reviewed-for="290906bf88c0f6a12d995faeea4c0ab18dad803aefe18bf89e349b3a45474f4a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Fine tunes camera yaw alignment.(+: right).

- **Negative:** Trims camera yaw to the left.
- **Positive:** Trims it to the right.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Evaluate on a flat, straight road at a steady speed, changing one step at a time and comparing whether left/right bias is reduced.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CameraYawTrimDeg -->

<!-- CARROT:SETTING:END CameraYawTrimDeg -->
