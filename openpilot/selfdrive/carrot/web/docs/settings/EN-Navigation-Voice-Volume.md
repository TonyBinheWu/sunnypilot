<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_SOUND" param="SoundLanguageVolume" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Navigation Voice Volume

**Menu:** System \> Sound

---

<!-- CARROT:SETTING:BEGIN SoundLanguageVolume -->
<a id="SoundLanguageVolume"></a>

## Navigation Voice Volume

`SoundLanguageVolume`

Relative gain for navigation turn, slowdown and 1–10 countdown voice prompts. 100% keeps the existing level, multiplied by general volume and ambient-noise adjustment. Applies within about one second without restart. Warning tones and engagement sounds keep their separate volume.

<!-- CARROT:AUTO:BEGIN SoundLanguageVolume -->
<!-- CARROT:AUTO:SOURCE facts="9f06316c87cef22a6cb87e69bb8067578152e5163fbb248fb380b60bb5ef1f50" semantic="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100%`
- **Range:** `5%` ~ `300%`
- **Step:** `5`
- **Display unit:** `%`
- **Menu:** System \> Sound
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoundLanguageVolume -->

<!-- CARROT:MANUAL:BEGIN SoundLanguageVolume -->
<!-- CARROT:REVIEW reviewed-for="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" reviewed-at="2026-11-13T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Raises or lowers navigation turn, slowdown and numeric countdown speech. Device playback multiplies general volume and ambient-noise adjustment; browser playback multiplies Web volume. Warning tones and engagement sounds keep their existing controls. Boosted device samples are limited to the output range.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Increase gradually while parked until navigation prompts are clear. Changes apply within about one second without restarting. A muted Web volume slider still mutes browser playback.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END SoundLanguageVolume -->

<!-- CARROT:SETTING:END SoundLanguageVolume -->
