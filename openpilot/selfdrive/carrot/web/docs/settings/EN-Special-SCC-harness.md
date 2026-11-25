<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_HYUNDAI" param="HyundaiCameraSCC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Special SCC harness

**Menu:** Vehicle & Hardware \> Hyundai·Kia

---

<!-- CARROT:SETTING:BEGIN HyundaiCameraSCC -->
<a id="HyundaiCameraSCC"></a>

## Special SCC harness

`HyundaiCameraSCC`

Use Vehicle default for a standard harness. 1: Long-con Vehicle, 2: Cruise State Sync (CAN-FD Vehicle), 3: Stock Cruise (CANFD Long harness) When off, SCC detected on the camera bus prompts you to enable this setting during a CAN error. Vehicles already configured for camera SCC are excluded. With CAN-FD CameraSCC, openpilot longitudinal control and corner radar enabled, valid CAN, Drive, released brakes and speed above 10.8 km/h allow periodic requests to switch on stock SCC MAIN. This applies independently of AutoEngage and Carrot cruise engagement, and these requests stop once MAIN is on. SET and standstill-resume requests retain the existing Carrot cruise engagement requirement. With CAN-FD CameraSCC and openpilot longitudinal control, the OEM SCC MAIN state used for cluster display is tracked separately from Carrot engagement intent. Steering activation follows AutoEngage initialization and the existing driver-button settings.

<!-- CARROT:AUTO:BEGIN HyundaiCameraSCC -->
<!-- CARROT:AUTO:SOURCE facts="e3708ec4a2916c9eef2160778ba6d04e2e67cefe0689aaf0352a708797a2d1aa" semantic="99524d08fffdef0918be8aff6ed855af38ce431ccfb14d86318363e4a5d1cbb4" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Vehicle default (`0`)
- **Range:** Vehicle default (`0`) ~ Stock SCC on modified harness (`3`)
- **Step:** `1`
- **Options:** `0` Vehicle default, `1` Modified longitudinal harness, `2` Cruise state sync, `3` Stock SCC on modified harness
- **Menu:** Vehicle & Hardware \> Hyundai·Kia
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HyundaiCameraSCC -->

<!-- CARROT:MANUAL:BEGIN HyundaiCameraSCC -->
<!-- CARROT:REVIEW reviewed-for="287a1e4a7254a0c59acf4e381efa7c629c34796276cbd8584241a52c4a779f28" reviewed-at="2026-11-04T12:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- `0` — Does not force camera SCC through this setting. Platform defaults and other longitudinal settings still apply.
- `1` — Uses the camera-SCC configuration and enables openpilot longitudinal control.
- `2` — Labeled for cruise-state sync; the current vehicle interface enables camera SCC and longitudinal control as it does for `1`.
- `3` — Uses the camera-SCC harness while leaving longitudinal control to stock cruise.

When this setting is off and camera SCC is not already applied, receiving `SCC_CONTROL` (CAN-FD) or `SCC12` (classic CAN) on the camera bus (bus2, or its multi-Panda equivalent) during the current onroad session adds **Enable CameraSCC** to CAN error alerts. The setting is never changed automatically, and existing disengagement and engagement blocking remain active.
With CAN-FD CameraSCC, openpilot longitudinal control and corner radar enabled, valid CAN, Drive, released brakes and speed above 10.8 km/h allow periodic requests to switch on stock SCC MAIN. This applies independently of AutoEngage and Carrot cruise engagement, and these requests stop once MAIN is on. SET and standstill-resume requests retain the existing Carrot cruise engagement requirement.

With CAN-FD CameraSCC and openpilot longitudinal control, the OEM SCC MAIN state used for cluster display is tracked separately from Carrot engagement intent. Steering activation follows AutoEngage initialization and the existing driver-button settings.

On EV6 HDA2 with the ADAS ECU harness and openpilot longitudinal control, the outgoing SCC message preserves fresh front-object fields received on physical E-CAN. If the factory transmitter stops, the cluster may have no central target. With factory cruise, the original SCC transmitter owns this display.

<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Confirm the vehicle specification and harness configuration, configure while parked, and verify SCC and lane-warning behavior on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> A mismatched vehicle, model year, HDA generation, or harness location can cause incorrect SCC or longitudinal behavior.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HyundaiCameraSCC -->

<!-- CARROT:SETTING:END HyundaiCameraSCC -->
