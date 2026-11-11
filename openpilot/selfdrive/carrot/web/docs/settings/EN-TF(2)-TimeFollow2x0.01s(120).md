<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="TFollowGap2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(2): TimeFollow2x0.01s(120)

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN TFollowGap2 -->
<a id="TFollowGap2"></a>

## TF(2): TimeFollow2x0.01s(120)

`TFollowGap2`

Base following time at cruise gap 2. 50=0.50 seconds. Speed TF and driving/deceleration adjustments apply.

<!-- CARROT:AUTO:BEGIN TFollowGap2 -->
<!-- CARROT:AUTO:SOURCE facts="fe6e62dd612f062f5059076d3954c018978d82b44fbd99a69a55bde9ab697470" semantic="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `120`
- **Range:** `40` ~ `300`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap2 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap2 -->
<!-- CARROT:REVIEW reviewed-for="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Base following time for cruise gap 2. Higher values increase the base gap; lower values reduce it. Speed TF and driving/deceleration adjustments apply.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Stored value 50 means 0.50 s. Gaps may share the same base TF with different lead responses. The path marker and metre label show the dynamically adjusted following target.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap2 -->

<!-- CARROT:SETTING:END TFollowGap2 -->
