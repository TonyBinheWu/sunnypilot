<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANEMODE" param="UseLaneLineSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Laneline: Speed(0)

**Menu:** Driving \> Steering \> Lane Mode

---

<!-- CARROT:SETTING:BEGIN UseLaneLineSpeed -->
<a id="UseLaneLineSpeed"></a>

## Laneline: Speed(0)

`UseLaneLineSpeed`

Uses lane mode above the set speed. Temporarily switches to laneless if model speed starts below 70% of measured speed or ends below 70% of its starting value; recovery requires about one second of acceptable conditions.

<!-- CARROT:AUTO:BEGIN UseLaneLineSpeed -->
<!-- CARROT:AUTO:SOURCE facts="3917490bdc292cc494f232eed809a06a3b5a471107ad2d8927beea3144565cf2" semantic="9482c046d017df996fafb1a43bed6362e51c89952cf90e9d08991f354560e6f3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0km/h`
- **Range:** `0km/h` ~ `200km/h`
- **Step:** `1`
- **Display unit:** `km/h`
- **Menu:** Driving \> Steering \> Lane Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseLaneLineSpeed -->

<!-- CARROT:MANUAL:BEGIN UseLaneLineSpeed -->
<!-- CARROT:REVIEW reviewed-for="c1d3fcc94fb373792b7f1ad242cc5c4b529b009b519117e53d940ac4ecd75043" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Switches to LaneMode when speed exceeds the set speed.

- **Higher:** Raises the applicable speed or speed threshold.
- **Lower:** Lowers the speed or threshold.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Repeat the same lane and curve while adjusting one item at a time, comparing path tracking, steering response, and smoothness together.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0` disables speed-based automatic switching. A lane-mode state selected by a button can still be maintained separately.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END UseLaneLineSpeed -->

<!-- CARROT:SETTING:END UseLaneLineSpeed -->
