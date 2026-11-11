<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_SCREEN" param="ClusterHudEncoder" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Encoder(0)

**Menu:** Display \> External HUD \> Screen & Camera

---

<!-- CARROT:SETTING:BEGIN ClusterHudEncoder -->
<a id="ClusterHudEncoder"></a>

## External HUD Encoder(0)

`ClusterHudEncoder`

0: Auto (Hardware H264 -\> Software H264 -\> JPEG) 1: JPEG 2: Hardware H264 3: Software H264 (ffmpeg/libx264)

<!-- CARROT:AUTO:BEGIN ClusterHudEncoder -->
<!-- CARROT:AUTO:SOURCE facts="650a65c989300d5a59656f501b61f9dca6b7ea606470280c2f3e6419339ad6c6" semantic="e7f0467150d4fda3feb1928b6ea87dac5141cb3e8bea9565855221b17bb9f0e6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Display \> External HUD \> Screen & Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudEncoder -->

<!-- CARROT:MANUAL:BEGIN ClusterHudEncoder -->
<!-- CARROT:REVIEW reviewed-for="bfbf70df61e7ca677ecf0cdf6ba8f498aa2ce1b76fb9fc7641423889a6f5810c" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Auto (Hardware H264 -> Software H264 -> JPEG)
- `1` — JPEG
- `2` — Hardware H264
- `3` — Software H264 (ffmpeg/libx264)

S3 Wi-Fi automatically selects H.264 after confirming firmware 1.2.0 support. This setting selects its hardware/software encoder, not the Wi-Fi codec. Auto initialization can fall back to JPEG if both H.264 backends fail; older S3 firmware uses JPEG.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Choose a mode while checking display latency, clarity, and CPU use on the external HUD.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudEncoder -->

<!-- CARROT:SETTING:END ClusterHudEncoder -->
