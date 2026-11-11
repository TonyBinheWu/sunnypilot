<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="AutoNaviRearCameraHoldDistance" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Rear Camera Post-pass Hold Distance (m)

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN AutoNaviRearCameraHoldDistance -->
<a id="AutoNaviRearCameraHoldDistance"></a>

## Rear Camera Post-pass Hold Distance (m)

`AutoNaviRearCameraHoldDistance`

When external navigation reports a rear speed or rear signal-and-speed camera (TMAP 75/76), retain the target-speed cap for this distance beyond the camera. The position is captured within the final 50 m and tracked by traveled distance even when guidance disappears or changes to the next item. Units are meters; 0 disables the extra hold. Increasing the value holds the cap farther beyond the camera. Stopping does not consume the distance. Disconnection, off-route status, or a new navigation session clears it. This distance does not apply to stock CAN warnings because their rear-camera type is not identified. Countdown completion does not end the speed hold.

<!-- CARROT:AUTO:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:AUTO:SOURCE facts="76318c5367973ebc5f1d96176a24349c92622aa5443bcc8662969f7332c7ddd4" semantic="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100`
- **Range:** `0` ~ `300`
- **Step:** `10`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:MANUAL:BEGIN AutoNaviRearCameraHoldDistance -->
<!-- CARROT:REVIEW reviewed-for="8b904f46c8e8a1e5c6c381366357034716287800c77b9036e8dc99eac2ec8689" reviewed-at="2026-09-13T09:14:58.799908+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When external navigation reports a rear speed or rear signal-and-speed camera (TMAP 75/76), retain the target-speed cap after passing. Increasing the value holds farther beyond the camera; decreasing it releases sooner. Zero disables the extra hold.

The position is captured within the final 50 m and tracked by traveled distance. The hold survives guidance removal or a switch to the next item, and stopping does not consume distance. A lower speed required by another control still takes precedence.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Displayed and stored values are in meters. The countdown ends at the camera; rear-camera hold distance is displayed separately. External disconnection, off-route status, a new session, a traveled-distance reset, or disabling camera control clears the hold.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Stock CAN does not identify rear-camera types, so this extra distance does not apply to it. The configured distance does not guarantee that measurement by the actual camera has ended.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviRearCameraHoldDistance -->

<!-- CARROT:SETTING:END AutoNaviRearCameraHoldDistance -->
