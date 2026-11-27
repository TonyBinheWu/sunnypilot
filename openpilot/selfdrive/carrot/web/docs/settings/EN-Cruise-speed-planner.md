<!-- CARROT:GENERATED schema="1" locale="en" group="DAILY_DRIVING" param="SunnyCruisePlanner" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise speed planner

**Menu:** Driving \> Start & Auto \> Daily driving

---

<!-- CARROT:SETTING:BEGIN SunnyCruisePlanner -->
<a id="SunnyCruisePlanner"></a>

## Cruise speed planner

`SunnyCruisePlanner`

Applies next drive with openpilot longitudinal control. 0 keeps the current planner. 1 uses sunnypilot cruise with the vehicle's radar and vision lead estimates. 2 uses the same planner with camera leads only. Enable DEC for scene-based switching in Experimental Mode.

<!-- CARROT:AUTO:BEGIN SunnyCruisePlanner -->
<!-- CARROT:AUTO:SOURCE facts="bd0365b9c49739f447106a0ecf4c7a5df051a474d10e7a346f76574c0c7d32c9" semantic="c38bc552088c099ef8b690307d86f5d076d3fce258662e3c4042e827d3a7bd3d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Current planner (`0`)
- **Range:** Current planner (`0`) ~ sunnypilot · camera leads (`2`)
- **Step:** `1`
- **Options:** `0` Current planner, `1` sunnypilot · vehicle sensors, `2` sunnypilot · camera leads
- **Menu:** Driving \> Start & Auto \> Daily driving
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SunnyCruisePlanner -->

<!-- CARROT:MANUAL:BEGIN SunnyCruisePlanner -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END SunnyCruisePlanner -->

<!-- CARROT:SETTING:END SunnyCruisePlanner -->
