<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_HYUNDAI" param="IsLdwsCar" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# HYUNDAI: LDWS ONLY CAR(0)

**Menu:** Vehicle & Hardware \> Hyundai·Kia

---

<!-- CARROT:SETTING:BEGIN IsLdwsCar -->
<a id="IsLdwsCar"></a>

## HYUNDAI: LDWS ONLY CAR(0)

`IsLdwsCar`

LDWS ONLY CAR

<!-- CARROT:AUTO:BEGIN IsLdwsCar -->
<!-- CARROT:AUTO:SOURCE facts="fdd08d4f282365ec09939acba7ffd20a2a5e37e145f893a5bfcc39fbe444c087" semantic="34f98ba7f7fd321a9bdd1b0e97bda0d45664cf5d320a3024bcfddb0784f5c889" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> Hyundai·Kia
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END IsLdwsCar -->

<!-- CARROT:MANUAL:BEGIN IsLdwsCar -->
<!-- CARROT:REVIEW reviewed-for="34f98ba7f7fd321a9bdd1b0e97bda0d45664cf5d320a3024bcfddb0784f5c889" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Uses the LDWS-only cluster option in legacy Hyundai/Kia `LKAS11` messages.
- **Off:** Keeps the vehicle-specific default LKAS/LFA cluster option.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Confirm the vehicle specification and harness configuration, configure while parked, and verify SCC and lane-warning behavior on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> A mismatched vehicle, model year, HDA generation, or harness location can cause incorrect SCC or longitudinal behavior.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END IsLdwsCar -->

<!-- CARROT:SETTING:END IsLdwsCar -->
