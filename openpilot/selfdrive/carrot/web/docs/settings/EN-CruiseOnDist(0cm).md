<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_AUTOCRUISE" param="CruiseOnDist" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CruiseOnDist(0cm)

**Menu:** Driving \> Start & Auto \> Auto Cruise

---

<!-- CARROT:SETTING:BEGIN CruiseOnDist -->
<a id="CruiseOnDist"></a>

## CruiseOnDist(0cm)

`CruiseOnDist`

Cruise ON when releasing the pedal and the front car gets close

<!-- CARROT:AUTO:BEGIN CruiseOnDist -->
<!-- CARROT:AUTO:SOURCE facts="60730388b34975f86e855da0fd94f6252da28d7d6f637e16f085ec9e249734e0" semantic="0c44a52dc53d02fb2b5c312b7ff88bdfab957c811fecd2c138ecd67868f032bb" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0cm`
- **Range:** `0cm` ~ `2500cm`
- **Step:** `50`
- **Display unit:** `cm`
- **Menu:** Driving \> Start & Auto \> Auto Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseOnDist -->

<!-- CARROT:MANUAL:BEGIN CruiseOnDist -->
<!-- CARROT:REVIEW reviewed-for="0c44a52dc53d02fb2b5c312b7ff88bdfab957c811fecd2c138ecd67868f032bb" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Cruise ON when releasing the pedal and the front car gets close.

- **Higher:** Increases the applicable distance or gap.
- **Lower:** Decreases the distance or gap.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time and compare the cruise activation point and set speed under the same start, accelerator, and lead-vehicle conditions.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CruiseOnDist -->

<!-- CARROT:SETTING:END CruiseOnDist -->
