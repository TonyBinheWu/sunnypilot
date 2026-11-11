<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_AUTOCRUISE" param="AutoGasCancelSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Auto Cruise: Gas Release Cancel Speed

**Menu:** Driving \> Start & Auto \> Auto Cruise

---

<!-- CARROT:SETTING:BEGIN AutoGasCancelSpeed -->
<a id="AutoGasCancelSpeed"></a>

## Auto Cruise: Gas Release Cancel Speed

`AutoGasCancelSpeed`

When releasing the accelerator pedal, cruise is canceled below this speed.

<!-- CARROT:AUTO:BEGIN AutoGasCancelSpeed -->
<!-- CARROT:AUTO:SOURCE facts="7f2e37ad7463b42b773ae3e130f4e0c6572d5f36367ecbd6eec30ea847abb267" semantic="93fa59e0c6761db851d9a73b8ceb501e211a24304f3b3f35a030a37bb4e5df3f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `30km/h`
- **Range:** `0km/h` ~ `200km/h`
- **Step:** `5`
- **Display unit:** `km/h`
- **Menu:** Driving \> Start & Auto \> Auto Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasCancelSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasCancelSpeed -->
<!-- CARROT:REVIEW reviewed-for="93fa59e0c6761db851d9a73b8ceb501e211a24304f3b3f35a030a37bb4e5df3f" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When releasing the accelerator pedal, cruise is canceled below this speed.

- **Higher:** Raises the applicable speed or speed threshold.
- **Lower:** Lowers the speed or threshold.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time and compare the cruise activation point and set speed under the same start, accelerator, and lead-vehicle conditions.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasCancelSpeed -->

<!-- CARROT:SETTING:END AutoGasCancelSpeed -->
