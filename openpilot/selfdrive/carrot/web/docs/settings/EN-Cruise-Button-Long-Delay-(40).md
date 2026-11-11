<!-- CARROT:GENERATED schema="1" locale="en" group="BUTTON_UNIT" param="CruiseButtonLongDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cruise Button Long Delay (40)

**Menu:** Driving \> Buttons & Presets \> Speed Units

---

<!-- CARROT:SETTING:BEGIN CruiseButtonLongDelay -->
<a id="CruiseButtonLongDelay"></a>

## Cruise Button Long Delay (40)

`CruiseButtonLongDelay`

Delay before the long-press action is triggered.

<!-- CARROT:AUTO:BEGIN CruiseButtonLongDelay -->
<!-- CARROT:AUTO:SOURCE facts="89834728d8a0e5d3f4e36c314b76bcc56b32301bbcc5f0ec63470c56dd50045e" semantic="7156b031dff48c8b2a99b76175c1620036d0ffbe8df7af1cc39a39690ddb9f59" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `40`
- **Range:** `30` ~ `100`
- **Step:** `10`
- **Menu:** Driving \> Buttons & Presets \> Speed Units
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseButtonLongDelay -->

<!-- CARROT:MANUAL:BEGIN CruiseButtonLongDelay -->
<!-- CARROT:REVIEW reviewed-for="7156b031dff48c8b2a99b76175c1620036d0ffbe8df7af1cc39a39690ddb9f59" reviewed-at="2026-09-22T02:17:36+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Delay before the long-press action is triggered.

- **Higher:** Increases the applicable time or delay.
- **Lower:** Decreases the time or delay.

This delay applies to the separate +/- buttons on Volkswagen. Separate SET/RES act once on release regardless of hold duration, without repeated speed adjustments.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Verify the set-speed change amount and timing for both a single press and a long press.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/buttons-presets.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseButtonLongDelay -->

<!-- CARROT:SETTING:END CruiseButtonLongDelay -->
