<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_NET" param="HotspotOnBoot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable HotSpot(0)

**Menu:** System \> Network & Map

---

<!-- CARROT:SETTING:BEGIN HotspotOnBoot -->
<a id="HotspotOnBoot"></a>

## Enable HotSpot(0)

`HotspotOnBoot`

Automatically starts the saved Wi-Fi hotspot and shares Internet when the SIM and cellular data connection are ready. Manually turning tethering off pauses automatic startup for this boot.

<!-- CARROT:AUTO:BEGIN HotspotOnBoot -->
<!-- CARROT:AUTO:SOURCE facts="ff6216f4ca2c64c5c50f391590632893490b0a340b7e726ea7003c62e81bed9f" semantic="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** System \> Network & Map
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HotspotOnBoot -->

<!-- CARROT:MANUAL:BEGIN HotspotOnBoot -->
<!-- CARROT:REVIEW reviewed-for="483a8e450bc5248e62520b76fc55c79fad20bff0753ad2f7a1540169a0b7c434" reviewed-at="2026-11-18T09:30:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When enabled, waits for a ready SIM and a fresh connected cellular data link, then starts the saved hotspot and Internet sharing. When disabled, stops the hotspot managed by this option.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

After updating and restarting once, changes apply within about five seconds. Keep the saved hotspot name and password; connect another device to verify both Carrot and Internet access. A failed activation retries with backoff.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Manually switching the hotspot off pauses automatic activation until this option is toggled off/on or the device restarts. Temporary cellular loss keeps the local network available. One Wi-Fi radio may switch from client to hotspot; the SIM plan, APN and carrier must permit tethering. No APN or roaming changes are made.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END HotspotOnBoot -->

<!-- CARROT:SETTING:END HotspotOnBoot -->
