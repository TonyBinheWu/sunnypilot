<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_CANFD" param="HDPuse" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Use HDP(CCNC)

**Menu:** Vehicle & Hardware \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN HDPuse -->
<a id="HDPuse"></a>

## Use HDP(CCNC)

`HDPuse`

1:While using APN, 2:Always

<!-- CARROT:AUTO:BEGIN HDPuse -->
<!-- CARROT:AUTO:SOURCE facts="82b995658173bf2c4f84726ee1af19eb1faf3e2b7066c20e43e84d70bf04bbb2" semantic="81f1a1ef230e556daa86169f16be0dde67d63f336598dd28620fff74b35b9139" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Vehicle & Hardware \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HDPuse -->

<!-- CARROT:MANUAL:BEGIN HDPuse -->
<!-- CARROT:REVIEW reviewed-for="81f1a1ef230e556daa86169f16be0dde67d63f336598dd28620fff74b35b9139" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Disables HDP message behavior.
- `1` — Uses HDP behavior only while APN is active.
- `2` — Always uses HDP behavior.
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
<!-- CARROT:MANUAL:END HDPuse -->

<!-- CARROT:SETTING:END HDPuse -->
