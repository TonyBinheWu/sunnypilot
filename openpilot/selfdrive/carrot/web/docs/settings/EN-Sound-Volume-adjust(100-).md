<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_SOUND" param="SoundVolumeAdjust" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Sound Volume adjust(100%)

**Menu:** System \> Sound

---

<!-- CARROT:SETTING:BEGIN SoundVolumeAdjust -->
<a id="SoundVolumeAdjust"></a>

## Sound Volume adjust(100%)

`SoundVolumeAdjust`

Adjusts general sound volume. The first audible DM warning uses at least 70% gain and the final warning always uses 100%, regardless of volume settings or ambient-noise attenuation.

<!-- CARROT:AUTO:BEGIN SoundVolumeAdjust -->
<!-- CARROT:AUTO:SOURCE facts="85b0aa41fc20c8b5ffabca96ad85fc1be87cc6a959c3a16116543fc8c04c5c45" semantic="dd82113cc6e9e733b3f10f9f9d9e6a61149a0ef90764fad9174d6f5fa06129d6" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0%`
- **Range:** `5%` ~ `200%`
- **Step:** `5`
- **Display unit:** `%`
- **Menu:** System \> Sound
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoundVolumeAdjust -->

<!-- CARROT:MANUAL:BEGIN SoundVolumeAdjust -->
<!-- CARROT:REVIEW reviewed-for="dd82113cc6e9e733b3f10f9f9d9e6a61149a0ef90764fad9174d6f5fa06129d6" reviewed-at="2026-09-28T23:41:56.644788+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Controls the volume multiplier for general alerts and prompts. Higher values make general prompts louder; lower values make them quieter.

The first audible DM warning has a 70% minimum gain; the final warning always uses 100%, regardless of volume settings or ambient-noise attenuation. This applies to modes 0 and 1 with camera or interaction monitoring.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

While parked, play prompts and verify language, general volume, and engage/disengage volume separately.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

The preceding visual-only notice remains silent. Navigation events sharing the same sound assets do not use the DM gain rule.

Percentages describe software output gain, not measured speaker sound pressure.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SoundVolumeAdjust -->

<!-- CARROT:SETTING:END SoundVolumeAdjust -->
