<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DM" param="DriverMonitoringEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable Driver Monitoring (Exception)

**Menu:** Vehicle & Hardware \> Driver Monitor

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringEnabled -->
<a id="DriverMonitoringEnabled"></a>

## Enable Driver Monitoring (Exception)

`DriverMonitoringEnabled`

Enabled by default, and leaving it enabled is recommended. This exception is intended only for devices without a DM camera or with a failed DM camera that cannot provide normal driver monitoring. Turning it off disables the normal-driving DM model and alerts, monitoring-triggered force deceleration, and lockout. Driving without driver monitoring may violate applicable laws, vehicle requirements, or terms of use; turn it off only after checking the requirements and accepting the safety responsibility.

<!-- CARROT:AUTO:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:AUTO:SOURCE facts="dca37ae66efdce4405c05a0b0663c94878ef7aef8c61720bc7061a4086e068fd" semantic="75de16e159e826f4dfe20f040bbaada4fc65960b24b5d45781569bb9bb118027" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `1`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> Driver Monitor
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringEnabled -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringEnabled -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END DriverMonitoringEnabled -->

<!-- CARROT:SETTING:END DriverMonitoringEnabled -->
