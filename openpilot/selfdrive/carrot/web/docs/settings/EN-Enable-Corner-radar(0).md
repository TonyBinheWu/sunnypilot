<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_RADAR" param="EnableCornerRadar" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable Corner radar(0)

**Menu:** Vehicle & Hardware \> Radar

---

<!-- CARROT:SETTING:BEGIN EnableCornerRadar -->
<a id="EnableCornerRadar"></a>

## Enable Corner radar(0)

`EnableCornerRadar`

1:Enable Corner radar, 2: Cutin Detection for CCNC car

<!-- CARROT:AUTO:BEGIN EnableCornerRadar -->
<!-- CARROT:AUTO:SOURCE facts="11ad710bcf1654461da63ae08a41114801a167ed7047b47714dc127528afea7a" semantic="f3344cc43f62d863ecb64a7db5ee5dc1890061598ea1a111001723780943390c" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Vehicle & Hardware \> Radar
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableCornerRadar -->

<!-- CARROT:MANUAL:BEGIN EnableCornerRadar -->
<!-- CARROT:REVIEW reviewed-for="f3344cc43f62d863ecb64a7db5ee5dc1890061598ea1a111001723780943390c" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Does not use corner radar.
- `1` — Uses supported corner-radar tracks.
- `2` — Uses corner-radar tracks and cut-in detection.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On a supported radar configuration, change one item at a time and verify detection and tracking under the same lead and cut-in conditions.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> Physical radar presence alone does not prove support. Verify message reception and tracking on the same vehicle configuration.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/radar.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END EnableCornerRadar -->

<!-- CARROT:SETTING:END EnableCornerRadar -->
