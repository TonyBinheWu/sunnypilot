<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_NET" param="HotspotOnBoot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable HotSpot(0)

**Menu:** System \> Network & Map

---

<!-- CARROT:SETTING:BEGIN HotspotOnBoot -->
<a id="HotspotOnBoot"></a>

## Enable HotSpot(0)

`HotspotOnBoot`

Feature to automatically enable hotspot when a USIM is inserted in COMMA

<!-- CARROT:AUTO:BEGIN HotspotOnBoot -->
<!-- CARROT:AUTO:SOURCE facts="d77a1734cbc66e6bdd936dec2762a0c273635f80f2a7fdac1c4a9dd1d8e9be37" semantic="f60b11ad1a9e01c9a2140827ce36a15ff5fc686b902d45a7c578afb846582f96" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** System \> Network & Map
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HotspotOnBoot -->

<!-- CARROT:MANUAL:BEGIN HotspotOnBoot -->
<!-- CARROT:REVIEW reviewed-for="f60b11ad1a9e01c9a2140827ce36a15ff5fc686b902d45a7c578afb846582f96" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** Requests automatic hotspot startup after boot when a cellular connection is available.
- **Off:** Does not enable the hotspot automatically at boot.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this while network connectivity is available, then verify it on the next connection or map view.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> Automatic hotspot startup requires a device with an available USIM and cellular network.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HotspotOnBoot -->

<!-- CARROT:SETTING:END HotspotOnBoot -->
