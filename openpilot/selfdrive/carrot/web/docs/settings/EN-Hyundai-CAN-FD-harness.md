<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_CANFD" param="CanfdHDA2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Hyundai CAN-FD harness

**Menu:** Vehicle & Hardware \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdHDA2 -->
<a id="CanfdHDA2"></a>

## Hyundai CAN-FD harness

`CanfdHDA2`

Applies at startup. Use automatic detection or select the installed harness.

<!-- CARROT:AUTO:BEGIN CanfdHDA2 -->
<!-- CARROT:AUTO:SOURCE facts="22a2320b9fd773663ac7a5c59fb0daab7bd17d257a2cc7fb34f353ecea3fe96d" semantic="a4d30a9a469e9c7a3be9b5bb5943a92f33fce83e193ba0e774e932a8a536e295" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Automatic (`2`)
- **Range:** Camera (HDA1) (`0`) ~ Automatic (`2`)
- **Step:** `1`
- **Options:** `0` Camera (HDA1), `1` ADAS ECU (HDA2), `2` Automatic
- **Menu:** Vehicle & Hardware \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdHDA2 -->

<!-- CARROT:MANUAL:BEGIN CanfdHDA2 -->
<!-- CARROT:REVIEW reviewed-for="2cd10469d96bc08a71fdfa257929f6cf6790a84cd48e7d2bcc55c07355d65caa" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Treats a Hyundai/Kia CAN FD vehicle as an HDA1 configuration.
- `1` — Uses the HDA2 CAN-bus configuration.
- `2` — Automatically identify the CAN-FD steering harness from the observed LKAS message and its length.
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
