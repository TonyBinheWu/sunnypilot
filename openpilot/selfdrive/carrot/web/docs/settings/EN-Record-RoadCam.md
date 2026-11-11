<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_RECORD_BASIC" param="RecordRoadCam" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Record RoadCam

**Menu:** System \> Record & Power \> Record & Power

---

<!-- CARROT:SETTING:BEGIN RecordRoadCam -->
<a id="RecordRoadCam"></a>

## Record RoadCam

`RecordRoadCam`

1: Standard Camera, 2: Standard Camera + Wide Camera

<!-- CARROT:AUTO:BEGIN RecordRoadCam -->
<!-- CARROT:AUTO:SOURCE facts="b89c534783bcf295e83520a8b44dc874a3ca1eb89979dacb5604a2e20873c324" semantic="ae86d8c67fad0c96a2cfaad63d1ccea6d5408fea17c62cd5a549ab67faf97d69" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** System \> Record & Power \> Record & Power
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RecordRoadCam -->

<!-- CARROT:MANUAL:BEGIN RecordRoadCam -->
<!-- CARROT:REVIEW reviewed-for="ae86d8c67fad0c96a2cfaad63d1ccea6d5408fea17c62cd5a549ab67faf97d69" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `1` — Standard Camera
- `2` — Standard Camera + Wide Camera
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check storage and power conditions, then verify the result at the next recording or offroad transition.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> Recording the wide camera also increases storage and memory-bandwidth use.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END RecordRoadCam -->

<!-- CARROT:SETTING:END RecordRoadCam -->
