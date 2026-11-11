<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_SCREEN" param="ShowPlotMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Debug Plot(0)

**Menu:** Display \> On-screen Info

---

<!-- CARROT:SETTING:BEGIN ShowPlotMode -->
<a id="ShowPlotMode"></a>

## Show Debug Plot(0)

`ShowPlotMode`

0:Off, 1:Accel, 2:Speed+Accel, 3:Model, 4:Lead accel/relative speed, 5:Lead accel/jerk, 6:Steer, 7:SteerA, 8:Curvature

<!-- CARROT:AUTO:BEGIN ShowPlotMode -->
<!-- CARROT:AUTO:SOURCE facts="4c12b809446b758db43a94e215c6cf746edfaed304a3ae51f1a08b2d84dc7895" semantic="7f2319fa7171e1573948b028f5354f0764f43be979f51b1511cabb15ab889343" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `0`
- **Range:** `0` ~ `8`
- **Step:** `1`
- **Menu:** Display \> On-screen Info
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPlotMode -->

<!-- CARROT:MANUAL:BEGIN ShowPlotMode -->
<!-- CARROT:REVIEW reviewed-for="fed9a1ccaab19da852200d90359bf75c4ff2d2c99e35ed39b63cfd57c001b853" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Off
- `1` — Accel
- `2` — Speed+Accel
- `3` — Model
- `4` — Lead
- `5` — Lead2
- `6` — Steer
- `7` — SteerA
- `8` — Curvature
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check placement and readability on the driving display and enable only the information you need.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPlotMode -->

<!-- CARROT:SETTING:END ShowPlotMode -->
