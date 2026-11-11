<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="TFollowGap1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(1): TimeFollow1x0.01s(110)

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN TFollowGap1 -->
<a id="TFollowGap1"></a>

## TF(1): TimeFollow1x0.01s(110)

`TFollowGap1`

Base following time at cruise gap 1. 50=0.50 seconds. Speed TF and driving/deceleration adjustments apply.

<!-- CARROT:AUTO:BEGIN TFollowGap1 -->
<!-- CARROT:AUTO:SOURCE facts="28f8b38062cf874dc2fec22a96778f721a23b3f54eef6b4a6aeef0675ffb7216" semantic="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `110`
- **Range:** `40` ~ `300`
- **Step:** `5`
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap1 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap1 -->
<!-- CARROT:REVIEW reviewed-for="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Base following time for cruise gap 1. Higher values increase the base gap; lower values reduce it. Speed TF and driving/deceleration adjustments apply.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Stored value 50 means 0.50 s. Gaps may share the same base TF with different lead responses. The path marker and metre label show the dynamically adjusted following target.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap1 -->

<!-- CARROT:SETTING:END TFollowGap1 -->
