<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="AutoNaviSpeedCtrlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NaviSpeedControlMode(2)

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedCtrlMode -->
<a id="AutoNaviSpeedCtrlMode"></a>

## NaviSpeedControlMode(2)

`AutoNaviSpeedCtrlMode`

0: Not Use, 1: Speed cam, 2: cam + speed bump, 3: cam + bump + apn speed cam Stock-navigation CAN mobile enforcement zones (blue circle, VehicleNaviCanControl) follow this value too: 3 decelerates and 2 or lower ignores the mobile-zone warning. A warning that also carries a fixed, signal or rear camera always decelerates.

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:AUTO:SOURCE facts="60b1737e96f9bdf17d9a78de685ce678952337df44325f554d15a94aff336c29" semantic="5b13349929a99c31fde786817313f0a97c7480cf55cdbce1da21739b3610e6d5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `2`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedCtrlMode -->
<!-- CARROT:REVIEW reviewed-for="5b13349929a99c31fde786817313f0a97c7480cf55cdbce1da21739b3610e6d5" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Not Use
- `1` — Speed cam
- `2` — cam + speed bump
- `3` — cam + bump + apn speed cam
Supported stock-navigation CAN mobile zones follow this setting too: mode 3 decelerates, while 2 or lower ignores mobile-zone warnings. Simultaneous fixed, signal or rear enforcement preserves deceleration.

<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time on the same speed limit and camera type, comparing deceleration start, completion point, and passing speed.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> Automatic deceleration works only when navigation data provides distance and speed-limit information for the selected event type.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedCtrlMode -->

<!-- CARROT:SETTING:END AutoNaviSpeedCtrlMode -->
