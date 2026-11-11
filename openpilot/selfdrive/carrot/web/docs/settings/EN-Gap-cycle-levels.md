<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="CruiseGapLevels" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Gap cycle levels

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN CruiseGapLevels -->
<a id="CruiseGapLevels"></a>

## Gap cycle levels

`CruiseGapLevels`

Number of levels cycled by the gap button, from 2 to the vehicle-supported maximum (the default). 2 uses TF1 and TF2; 3 uses TF1 through TF3. Applies on the next gap-button press and preserves unused TF and following responsiveness values. Applies with openpilot longitudinal control; stock ACC keeps its own levels.

<!-- CARROT:AUTO:BEGIN CruiseGapLevels -->
<!-- CARROT:AUTO:SOURCE facts="9e24b1e1808eee8023c207e39c845716059c2580cf74754ce5f66043908fc13d" semantic="0b2beba3c4ae3136707b59ae19b20a500b34caf419dd7fc699481622c446c9e1" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** 4 levels (`4`)
- **Range:** 2 levels (`2`) ~ 4 levels (`4`)
- **Step:** `1`
- **Options:** `2` 2 levels, `3` 3 levels, `4` 4 levels
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseGapLevels -->

<!-- CARROT:MANUAL:BEGIN CruiseGapLevels -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CruiseGapLevels -->

<!-- CARROT:SETTING:END CruiseGapLevels -->
