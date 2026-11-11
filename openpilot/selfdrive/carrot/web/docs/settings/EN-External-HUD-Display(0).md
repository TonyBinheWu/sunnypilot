<!-- CARROT:GENERATED schema="1" locale="en" group="HUD_BASIC" param="ClusterHud" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# External HUD Display(0)

**Menu:** Display \> External HUD \> Basic

---

<!-- CARROT:SETTING:BEGIN ClusterHud -->
<a id="ClusterHud"></a>

## External HUD Display(0)

`ClusterHud`

0: Off 1: TURZX 9.2 inch Applies to a USB HUD connected to this device. A USB HUD connected to Jetson starts automatically regardless of this setting. The display turns off with ignition; HUD Debug controls always-on output. Supported Jetson runtimes receive HUD, navigation and signal information over USB during inference. Older receivers retain their Wi-Fi path until updated. Device output is 10 FPS, or 5 FPS with an active eGPU. Jetson targets 10 FPS.

<!-- CARROT:AUTO:BEGIN ClusterHud -->
<!-- CARROT:AUTO:SOURCE facts="9873e980f18a309e8e86af56441593317405c1fff4ae054352bce42f2abb7632" semantic="9edf824457ea89ad8d62580c7ca4d5e4fc5c4e9c21e0b81860547c9d4b2bb10e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Display \> External HUD \> Basic
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHud -->

<!-- CARROT:MANUAL:BEGIN ClusterHud -->
<!-- CARROT:REVIEW reviewed-for="17e8e51b49d27978d564c982b7216d47db6b18c9d4a636e239f4306d3b9cdf96" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Switches a direct USB or registered S3 HUD on or off. A HUD attached to Jetson starts automatically regardless of this setting.

Updated C4 and S3 firmware 1.2.0 automatically use H.264; older firmware or missing capability replies use JPEG. The target is 15 FPS, capped at 10 FPS with an active eGPU; actual speed depends on content and wireless conditions.

[Installation, firmware and registration](https://upload.shind0.synology.me/models/carrot-s3/index.html) explains the one-time S3 1.2.0 update. Wi-Fi/C4 registration is preserved, and the display reconnects on the same 2.4 GHz network.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

The display normally turns off with ignition. Use an always-on HUD Debug mode for offroad output; brightness and layout still use the existing HUD settings.

The Jetson HUD shows Jetson temperature and warns near its configured thermal limits. Check the fan and ventilation when warned.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHud -->

<!-- CARROT:SETTING:END ClusterHud -->
