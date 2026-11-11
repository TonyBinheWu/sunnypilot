<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_DRIVE_MODE" param="MyDrivingMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# DrivingMode:Init(3)

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Drive Mode

---

<!-- CARROT:SETTING:BEGIN MyDrivingMode -->
<a id="MyDrivingMode"></a>

## DrivingMode:Init(3)

`MyDrivingMode`

1: Eco - Maximum acceleration ×0.9, time gap ×1.1, lead response capped at 2. 2: Safe - Maximum acceleration ×0.8, time gap ×1.2, lead response capped at 3, with more allowance for earlier gentle braking. 3: Normal - Baseline acceleration and gap with the selected lead response. 4: High - Maximum acceleration ×1.2 with the selected response; traffic-light stopping is disabled. There is no separate mode-specific jerk adjustment. Mode gap allowance releases gradually. Lower response choices and 0 are never raised.

<!-- CARROT:AUTO:BEGIN MyDrivingMode -->
<!-- CARROT:AUTO:SOURCE facts="fd438837b148dae2dca5e1e15e920b3fdce5cec978263ec66aa47357cea83bb3" semantic="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `3`
- **Range:** `1` ~ `4`
- **Step:** `1`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Drive Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingMode -->

<!-- CARROT:MANUAL:BEGIN MyDrivingMode -->
<!-- CARROT:REVIEW reviewed-for="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" reviewed-at="2026-09-13T10:16:28.802623+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Eco uses maximum acceleration ×0.9 and time gap ×1.1. Safe uses maximum acceleration ×0.8, time gap ×1.2 and more allowance for gentle stopping. Normal uses the baseline; High applies maximum acceleration ×1.2 and disables traffic stop/go detection.

After resolving the common or gap-specific response, Eco caps it at 2 and Safe at 3. Normal and High retain the selected value; lower choices and 0 are never raised, and stored values are unchanged.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Compare acceleration and deceleration response between modes at the same speed and lead-vehicle condition.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

There is no separate mode-specific jerk adjustment; the effective lead response controls boost and temporary gap recovery. Decreasing mode gap multipliers release at 0.05 per second, without separately delaying an explicit driver selection of a smaller gap.

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MyDrivingMode -->

<!-- CARROT:SETTING:END MyDrivingMode -->
