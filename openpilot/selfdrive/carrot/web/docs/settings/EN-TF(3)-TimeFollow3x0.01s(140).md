<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="TFollowGap3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(3): TimeFollow3x0.01s(140)

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN TFollowGap3 -->
<a id="TFollowGap3"></a>

## TF(3): TimeFollow3x0.01s(140)

`TFollowGap3`

Base following time at cruise gap 3. 50=0.50 seconds. Speed TF and driving/deceleration adjustments apply.

<!-- CARROT:AUTO:BEGIN TFollowGap3 -->
<!-- CARROT:AUTO:SOURCE facts="fec2c016770cc483f2e2ec3043ce1ee9f80c012acea116c5c228e845ce0f49b8" semantic="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `140`
- **Range:** `40` ~ `300`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap3 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap3 -->
<!-- CARROT:REVIEW reviewed-for="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Base following time for cruise gap 3. Higher values increase the base gap; lower values reduce it. Speed TF and driving/deceleration adjustments apply.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Stored value 50 means 0.50 s. Gaps may share the same base TF with different lead responses. The path marker and metre label show the dynamically adjusted following target.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap3 -->

<!-- CARROT:SETTING:END TFollowGap3 -->
