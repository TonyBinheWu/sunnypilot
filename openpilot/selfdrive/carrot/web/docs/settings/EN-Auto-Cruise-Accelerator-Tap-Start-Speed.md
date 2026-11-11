<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_AUTOCRUISE" param="AutoGasTokSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Auto Cruise: Accelerator Tap Start Speed

**Menu:** Driving \> Start & Auto \> Auto Cruise

---

<!-- CARROT:SETTING:BEGIN AutoGasTokSpeed -->
<a id="AutoGasTokSpeed"></a>

## Auto Cruise: Accelerator Tap Start Speed

`AutoGasTokSpeed`

Operates only above the set speed — GasTab : Tap the accelerator pedal for 0.6 seconds

<!-- CARROT:AUTO:BEGIN AutoGasTokSpeed -->
<!-- CARROT:AUTO:SOURCE facts="0190e0082c146f84306bb56095497f75f89a22893d56c4db369eeffb222c746a" semantic="566c9988c19eba63fd6ef647f6a0e4a6d6ba01d071de04c633eb540cc2cf4441" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0km/h`
- **Range:** `0km/h` ~ `200km/h`
- **Step:** `5`
- **Display unit:** `km/h`
- **Menu:** Driving \> Start & Auto \> Auto Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasTokSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasTokSpeed -->
<!-- CARROT:REVIEW reviewed-for="566c9988c19eba63fd6ef647f6a0e4a6d6ba01d071de04c633eb540cc2cf4441" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Operates only above the set speed — GasTab : Tap the accelerator pedal for 0.6 seconds.

- **Higher:** Raises the applicable speed or speed threshold.
- **Lower:** Lowers the speed or threshold.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time and compare the cruise activation point and set speed under the same start, accelerator, and lead-vehicle conditions.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasTokSpeed -->

<!-- CARROT:SETTING:END AutoGasTokSpeed -->
