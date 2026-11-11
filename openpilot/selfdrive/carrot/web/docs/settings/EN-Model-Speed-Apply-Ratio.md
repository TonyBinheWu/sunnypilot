<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CURVE" param="ApplyModelSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Model Speed Apply Ratio

**Menu:** Driving \> Speed & Decel \> Curve & Turn

---

<!-- CARROT:SETTING:BEGIN ApplyModelSpeed -->
<a id="ApplyModelSpeed"></a>

## Model Speed Apply Ratio

`ApplyModelSpeed`

Applies the model-calculated driving speed by the set ratio.

<!-- CARROT:AUTO:BEGIN ApplyModelSpeed -->
<!-- CARROT:AUTO:SOURCE facts="6891e5d6f7d7baf2195a0e8e9a59c7f3c6e8a8fdbd13e4daca55bfe29a8a96db" semantic="8039edb57e0c4c2bb0d6e9911d247c64a6f0c42f2e912402bc572f0a4701f388" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `-120%` ~ `120%`
- **Step:** `1`
- **Display unit:** `%`
- **Menu:** Driving \> Speed & Decel \> Curve & Turn
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ApplyModelSpeed -->

<!-- CARROT:MANUAL:BEGIN ApplyModelSpeed -->
<!-- CARROT:REVIEW reviewed-for="8039edb57e0c4c2bb0d6e9911d247c64a6f0c42f2e912402bc572f0a4701f388" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Does not apply model-predicted speed to the cruise set speed.
- **Positive:** Raises the set speed when the scaled model prediction is above the current set speed, capped at 110% of the road speed limit.
- **Negative:** Applies the scaled model target directly, so the set speed can drop sharply.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Adjust one item at a time on the same curve and route-guidance condition, comparing the target before entry and the speed through the curve.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0` does not blend model driving speed into the target. Positive and negative values apply the model-speed blend in opposite directions.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ApplyModelSpeed -->

<!-- CARROT:SETTING:END ApplyModelSpeed -->
