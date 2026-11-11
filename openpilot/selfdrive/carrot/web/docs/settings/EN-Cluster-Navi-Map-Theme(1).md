<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_BASIC" param="ClusterNaviMapTheme" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Cluster Navi Map Theme(1)

**Menu:** Display \> External HUD \> Basic

---

<!-- CARROT:SETTING:BEGIN ClusterNaviMapTheme -->
<a id="ClusterNaviMapTheme"></a>

## Cluster Navi Map Theme(1)

`ClusterNaviMapTheme`

0: Auto 1: Dark 2: Light The external navigation app reconnects automatically when changed.

<!-- CARROT:AUTO:BEGIN ClusterNaviMapTheme -->
<!-- CARROT:AUTO:SOURCE facts="8e53878d1ed48fa1ac97a0deb9dd74eb867242c3278c67fd6c1901c32ba27599" semantic="22c25adc7668b0b1e6f02c8676e96b5d9f45276bc7802f5e0fdc596b6f12bb21" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Dark (`1`)
- **Range:** Auto (`0`) ~ Light (`2`)
- **Step:** `1`
- **Options:** `0` Auto, `1` Dark, `2` Light
- **Menu:** Display \> External HUD \> Basic
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterNaviMapTheme -->

<!-- CARROT:MANUAL:BEGIN ClusterNaviMapTheme -->
<!-- CARROT:REVIEW reviewed-for="87294e7f3ad7b929ada06c18c8a6c0c4690b9fd5ce3b8f3faf54c31dffd43ba4" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Auto
- `1` — Dark
- `2` — Light / The external navigation app reconnects automatically when changed
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
<!-- CARROT:MANUAL:END ClusterNaviMapTheme -->

<!-- CARROT:SETTING:END ClusterNaviMapTheme -->
