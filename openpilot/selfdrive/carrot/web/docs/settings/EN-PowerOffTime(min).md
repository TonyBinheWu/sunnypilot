<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_RECORD_BASIC" param="MaxTimeOffroadMin" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# PowerOffTime(min)

**Menu:** System \> Record & Power \> Record & Power

---

<!-- CARROT:SETTING:BEGIN MaxTimeOffroadMin -->
<a id="MaxTimeOffroadMin"></a>

## PowerOffTime(min)

`MaxTimeOffroadMin`

When the engine is turned off and the specified time elapses, the comma device will shut down.

<!-- CARROT:AUTO:BEGIN MaxTimeOffroadMin -->
<!-- CARROT:AUTO:SOURCE facts="445fe36a942e40231de6da1e1ea554f9e630b3c98593a05d17f644d2f1b15cd8" semantic="3c6bd1ba89c52b9eb29c02d193878767c4a527a2cd122355fc4d67ca6d8eeaa8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `60min`
- **Range:** `0min` ~ `3000min`
- **Step:** `10`
- **Display unit:** `min`
- **Menu:** System \> Record & Power \> Record & Power
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MaxTimeOffroadMin -->

<!-- CARROT:MANUAL:BEGIN MaxTimeOffroadMin -->
<!-- CARROT:REVIEW reviewed-for="3c6bd1ba89c52b9eb29c02d193878767c4a527a2cd122355fc4d67ca6d8eeaa8" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When the engine is turned off and the specified time elapses, the comma device will shut down.

- **Higher:** Increases the applicable time or delay.
- **Lower:** Decreases the time or delay.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check storage and power conditions, then verify the result at the next recording or offroad transition.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END MaxTimeOffroadMin -->

<!-- CARROT:SETTING:END MaxTimeOffroadMin -->
