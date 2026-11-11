<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="TFollowDecelBoost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Deceleration Gap Margin (0%)

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN TFollowDecelBoost -->
<a id="TFollowDecelBoost"></a>

## Deceleration Gap Margin (0%)

`TFollowDecelBoost`

Adds a single deceleration-dependent margin to the baseline target gap without accumulating it during sustained braking. Higher values add more space. Extra margin releases progressively as braking eases. 0% disables added margin; any already-applied margin releases gradually. Baseline gap-reduction hold during deceleration remains active.

<!-- CARROT:AUTO:BEGIN TFollowDecelBoost -->
<!-- CARROT:AUTO:SOURCE facts="862b1817f57d0dab48edffd1eaefd7233d215176bab065e0348aff47fb78594a" semantic="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `0%` ~ `100%`
- **Step:** `10`
- **Display unit:** `%`
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowDecelBoost -->

<!-- CARROT:MANUAL:BEGIN TFollowDecelBoost -->
<!-- CARROT:REVIEW reviewed-for="a003496b606637110045bb4c8096e6fd7af91b9b8c2778f41be61772125c46ca" reviewed-at="2026-09-09T08:56:50.212594+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Adds one deceleration-dependent margin to the baseline target gap without repeatedly accumulating it during sustained braking. Higher values add more space; lower values add less.

The extra margin releases progressively as braking eases and updates promptly when braking strengthens. Disabling the setting gradually releases already-applied margin while preserving baseline gap-reduction hold during braking.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use this to adjust spacing during deceleration. Changing the value does not change the configured base following gaps.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:MANUAL:END TFollowDecelBoost -->

<!-- CARROT:SETTING:END TFollowDecelBoost -->
