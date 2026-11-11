<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_DRIVE_MODE" param="MyDrivingModeAuto" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# DrivingMode: Auto

**Menu:** Driving \> Cruise & Gap \> Accel Profile \> Drive Mode

---

<!-- CARROT:SETTING:BEGIN MyDrivingModeAuto -->
<a id="MyDrivingModeAuto"></a>

## DrivingMode: Auto

`MyDrivingModeAuto`

0: Manual, 1: Normal↔Safe, 2: Eco↔Safe. Stopping-lead approaches enter Safe promptly; sustained slow following also selects Safe. Outside a stopping approach, lead acceleration above 1.0m/s² for about 0.5 seconds restores the base mode. Otherwise, three seconds of flow recovery or a clear road while moving restores it. High is never selected automatically.

<!-- CARROT:AUTO:BEGIN MyDrivingModeAuto -->
<!-- CARROT:AUTO:SOURCE facts="c155b8b1b8abacd1f737b5c14f80505ec0cd41600262cdf2864d14e78397be18" semantic="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Cruise & Gap \> Accel Profile \> Drive Mode
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingModeAuto -->

<!-- CARROT:MANUAL:BEGIN MyDrivingModeAuto -->
<!-- CARROT:REVIEW reviewed-for="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" reviewed-at="2026-09-27T14:30:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

`0` is manual, `1` selects Normal↔Safe, and `2` selects Eco↔Safe. Safe follows about 0.3 seconds of a stopping-lead approach or eight seconds of slow following. Outside a stopping approach, lead acceleration above 1.0 m/s² for about 0.5 seconds restores Normal/Eco. Otherwise, recovery requires three seconds of restored flow or four seconds with no lead at 15 km/h or above.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Compare acceleration and deceleration response between modes at the same speed and lead-vehicle condition.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> Manually changing the stored driving mode suspends automatic selection until the planner restarts. High is never selected automatically, and lead loss while stopped does not restore the base mode.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MyDrivingModeAuto -->

<!-- CARROT:SETTING:END MyDrivingModeAuto -->
