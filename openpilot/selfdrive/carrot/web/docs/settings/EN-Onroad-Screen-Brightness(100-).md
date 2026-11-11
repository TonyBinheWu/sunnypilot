<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_BRIGHT" param="ShowCustomBrightness" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Onroad Screen Brightness(100%)

**Menu:** Display \> Brightness & View

---

<!-- CARROT:SETTING:BEGIN ShowCustomBrightness -->
<a id="ShowCustomBrightness"></a>

## Onroad Screen Brightness(100%)

`ShowCustomBrightness`

Screen brightness ratio ~10s after driving starts 0: Auto adjust by ambient light 100: Always max brightness

<!-- CARROT:AUTO:BEGIN ShowCustomBrightness -->
<!-- CARROT:AUTO:SOURCE facts="454d3b901b90a60ecfa7557a05de6fcc9a7848d94ab10f3bb884eaee0e9fb359" semantic="fc03de2baf9a00998b9705313c1101cb5d556a9067d5a4ab5b539596ebe94454" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100%`
- **Range:** `0%` ~ `100%`
- **Step:** `5`
- **Display unit:** `%`
- **Menu:** Display \> Brightness & View
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowCustomBrightness -->

<!-- CARROT:MANUAL:BEGIN ShowCustomBrightness -->
<!-- CARROT:REVIEW reviewed-for="fc03de2baf9a00998b9705313c1101cb5d556a9067d5a4ab5b539596ebe94454" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Auto adjust by ambient light
- `100` — Always max brightness
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

After onroad brightness stabilizes, check camera/model visibility and glare.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowCustomBrightness -->

<!-- CARROT:SETTING:END ShowCustomBrightness -->
