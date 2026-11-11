<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_NET" param="MapboxStyle" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# MapboxStyle

**Menu:** System \> Network & Map

---

<!-- CARROT:SETTING:BEGIN MapboxStyle -->
<a id="MapboxStyle"></a>

## MapboxStyle

`MapboxStyle`

0: Default Background, 1: Dark Background, 2: Satellite Map

<!-- CARROT:AUTO:BEGIN MapboxStyle -->
<!-- CARROT:AUTO:SOURCE facts="44db0f54c717c3cc29a8b9ab7478a19ed752e6bcfef7f6aaa52b8663008ac71f" semantic="4fa181aa8b1ee134ff859a4de7be4d66b9ab4e4a0dbaef9ee15a589c4024141e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** System \> Network & Map
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MapboxStyle -->

<!-- CARROT:MANUAL:BEGIN MapboxStyle -->
<!-- CARROT:REVIEW reviewed-for="4fa181aa8b1ee134ff859a4de7be4d66b9ab4e4a0dbaef9ee15a589c4024141e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Default Background
- `1` — Dark Background
- `2` — Satellite Map
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this while network connectivity is available, then verify it on the next connection or map view.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END MapboxStyle -->

<!-- CARROT:SETTING:END MapboxStyle -->
