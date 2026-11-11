<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_CANFD" param="CanfdHDA2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CANFD HDA2(0)

**Menu:** Vehicle & Hardware \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdHDA2 -->
<a id="CanfdHDA2"></a>

## CANFD HDA2(0)

`CanfdHDA2`

0:HDA1, 1: HDA2

<!-- CARROT:AUTO:BEGIN CanfdHDA2 -->
<!-- CARROT:AUTO:SOURCE facts="08166219b234cafad7198d267cd8e0b21a8f3ab693a042a74a3c098e95244eed" semantic="2cd10469d96bc08a71fdfa257929f6cf6790a84cd48e7d2bcc55c07355d65caa" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdHDA2 -->

<!-- CARROT:MANUAL:BEGIN CanfdHDA2 -->
<!-- CARROT:REVIEW reviewed-for="2cd10469d96bc08a71fdfa257929f6cf6790a84cd48e7d2bcc55c07355d65caa" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Treats a Hyundai/Kia CAN FD vehicle as an HDA1 configuration.
- `1` — Uses the HDA2 CAN-bus configuration.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Confirm the vehicle's HDA and CAN FD configuration, configure while parked, and check the related feature and any faults on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> An unverified CAN FD configuration can cause vehicle warnings or CAN faults.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CanfdHDA2 -->

<!-- CARROT:SETTING:END CanfdHDA2 -->
