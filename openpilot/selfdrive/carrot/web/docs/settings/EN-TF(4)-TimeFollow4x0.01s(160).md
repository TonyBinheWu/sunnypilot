<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="TFollowGap4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(4): TimeFollow4x0.01s(160)

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN TFollowGap4 -->
<a id="TFollowGap4"></a>

## TF(4): TimeFollow4x0.01s(160)

`TFollowGap4`

Base following time at cruise gap 4. 50=0.50 seconds. Speed TF and driving/deceleration adjustments apply.

<!-- CARROT:AUTO:BEGIN TFollowGap4 -->
<!-- CARROT:AUTO:SOURCE facts="7a37a8d8c9d7f38b8948f2c98b6c13271f6ff8ddb877b5c52fcb2313494eda9e" semantic="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `160`
- **Range:** `40` ~ `300`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap4 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap4 -->
<!-- CARROT:REVIEW reviewed-for="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Base following time for cruise gap 4. Higher values increase the base gap; lower values reduce it. Speed TF and driving/deceleration adjustments apply.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Stored value 50 means 0.50 s. Gaps may share the same base TF with different lead responses. The path marker and metre label show the dynamically adjusted following target.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap4 -->

<!-- CARROT:SETTING:END TFollowGap4 -->
