<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_CANFD" param="CanfdBlinkerControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CAN-FD SPAS indicators (trial)

**Menu:** Vehicle & Hardware \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdBlinkerControl -->
<a id="CanfdBlinkerControl"></a>

## CAN-FD SPAS indicators (trial)

`CanfdBlinkerControl`

Use comma SPAS indicators on Hyundai/Kia/Genesis CAN-FD vehicles with matching ECAN SPAS1/2 and valid driver input. Default OFF; reboot required. Disables the Jetson USB2CAN blinker path. The parking ECU is temporarily paused only during a requested signal and restored afterwards. Existing AutoBlinkerControl modes apply. Vehicle acceptance is required.

<!-- CARROT:AUTO:BEGIN CanfdBlinkerControl -->
<!-- CARROT:AUTO:SOURCE facts="ce6b3a2c6ecf74c755f5a2bdb5c27920f82af55eef22e5baafed17d133d8e135" semantic="b9c8da21ba0961eca86e2eeeedd9232360297164deac532d95f215a0433ae12c" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdBlinkerControl -->

<!-- CARROT:MANUAL:BEGIN CanfdBlinkerControl -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CanfdBlinkerControl -->

<!-- CARROT:SETTING:END CanfdBlinkerControl -->
