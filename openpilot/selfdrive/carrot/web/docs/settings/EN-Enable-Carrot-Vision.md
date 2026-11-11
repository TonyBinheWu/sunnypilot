<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable Carrot Vision

**Menu:** Vehicle & Hardware \> Driver Monitor

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## Enable Carrot Vision

`CarrotVisionEnabled`

Enables web road-camera streaming independently of driver monitoring, including while the external HUD is enabled. Simultaneous video use may increase device load.

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="cab86478aac061cfa65098823e247abcb048ec3c232d6a1fe9b1f5c0ed2e1e3f" semantic="06ceb617dbe739cddd0239009397024736b16a64f730822966da6da92c24437d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Off (`0`)
- **Range:** Off (`0`) ~ On (`1`)
- **Step:** `1`
- **Options:** `0` Off, `1` On
- **Menu:** Vehicle & Hardware \> Driver Monitor
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotVisionEnabled -->

<!-- CARROT:MANUAL:BEGIN CarrotVisionEnabled -->
<!-- CARROT:REVIEW reviewed-for="196e1f296cc743239e491c11d519cea88fbf7bde06ad6f1fe40b377fe6758e07" reviewed-at="2026-09-28T07:45:02.976276+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Enabling permits web road-camera streaming; disabling stops it. This setting is independent of driver monitoring.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Enable when using web road video. Carrot Vision is unavailable while the USB cluster is enabled.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

The old DisableDM streaming choice is migrated to this setting once. Migration does not disable monitoring or enable experimental mode.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
