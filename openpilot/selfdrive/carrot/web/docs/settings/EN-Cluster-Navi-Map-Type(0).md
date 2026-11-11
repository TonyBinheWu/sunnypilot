<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_BASIC" param="ClusterNaviMapType" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cluster Navi Map Type(0)

**Menu:** Display \> External HUD \> Basic

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapType -->
<a id="ClusterNaviMapType"></a>

## Cluster Navi Map Type(0)

`ClusterNaviMapType`

0: Normal map 1: Satellite map The external navigation app reconnects automatically when changed.

<!-- CARROT:AUTO:BEGIN ClusterNaviMapType -->
<!-- CARROT:AUTO:SOURCE facts="331be75e92618b04e45ca9a2fee21db02970f87272c86a58fa4963a2efff6984" semantic="74a31937ac7dd81fe72e06f0f41520736d6558235984d4865a8b22153b7a32f0" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Normal map (`0`)
- **Range:** Normal map (`0`) ~ Satellite map (`1`)
- **Step:** `1`
- **Options:** `0` Normal map, `1` Satellite map
- **Menu:** Display \> External HUD \> Basic
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapType -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapType -->
<!-- CARROT:REVIEW reviewed-for="cecc953658fa7976938bc4de62a707ed52b4d1c7a0755356e26cbb8c2f7e090e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Normal map
- `1` — Satellite map / The external navigation app reconnects automatically when changed
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this with the external HUD connected, then verify orientation, brightness, and map connection.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> Changing this automatically reconnects the external navigation source.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ClusterNaviMapType -->

<!-- CARROT:SETTING:END ClusterNaviMapType -->
