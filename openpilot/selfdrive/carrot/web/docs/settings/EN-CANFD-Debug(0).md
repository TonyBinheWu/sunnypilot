<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_CANFD" param="CanfdDebug" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CANFD Debug(0)

**Menu:** Vehicle & Hardware \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdDebug -->
<a id="CanfdDebug"></a>

## CANFD Debug(0)

`CanfdDebug`

CANFD Debug(0)

<!-- CARROT:AUTO:BEGIN CanfdDebug -->
<!-- CARROT:AUTO:SOURCE facts="007612cf89aeb6d77a1890f22b4ea7e732f059e30be7e759f5a8669572cff242" semantic="12eb933ab9caf967e2a49d1d4a6b0a39f236a64333398e155efc78871fd68181" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `-1` ~ `128`
- **Step:** `1`
- **Menu:** Vehicle & Hardware \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdDebug -->

<!-- CARROT:MANUAL:BEGIN CanfdDebug -->
<!-- CARROT:REVIEW reviewed-for="12eb933ab9caf967e2a49d1d4a6b0a39f236a64333398e155efc78871fd68181" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Passes the value to the Hyundai/Kia CCNC CAN FD message generator as a diagnostic mode. It is not a normal user feature, and per-value behavior is not a stable user-facing contract.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Confirm the vehicle's HDA and CAN FD configuration, configure while parked, and check the related feature and any faults on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> This is a developer diagnostic value passed directly into vehicle CAN message generation. Keep the default unless diagnosing that path.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CanfdDebug -->

<!-- CARROT:SETTING:END CanfdDebug -->
