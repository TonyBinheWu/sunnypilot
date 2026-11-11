<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DM" param="DriverMonitoringMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Driver Monitoring Mode

**Menu:** Vehicle & Hardware \> Driver Monitor

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringMode -->
<a id="DriverMonitoringMode"></a>

## Driver Monitoring Mode

`DriverMonitoringMode`

0: Standard; 1: Experimental. Experimental mode may violate law; use only in controlled tests. Without a camera, base alerts are 15/30/45 seconds; experimental mode uses 30/60/90 on a verified empty straight road. Only the transition from no moving traffic to confirmed moving traffic starts 20 seconds of standard monitoring. Additional or continuously observed vehicles do not extend it; experimental monitoring resumes afterwards. During the hold, camera interaction grace, special forward-attention resets and detection relaxation are suspended, and previous grace ends. Camera mode 0 retains comma behavior. Camera mode 1 uses 10/16/26 seconds, or 20/32/52 on an empty road, with 20% wider head-pose tolerance. Driver/BT input resets monitoring and defers camera warnings for 45 or 90 seconds before camera monitoring starts. This also delays sleep, eye-closure and phone warnings. Two seconds of confident forward attention resets camera monitoring. Input cannot clear terminal alerts or lockout. Camera faults automatically select interaction monitoring. Mode 0 is not legal certification. Mode changes apply live at roughly half-second intervals without rebooting. Switching preserves accumulated monitoring time, warning counts and lockout, and ends the previous interaction grace and forward-attention streak. Original STEER\_TOUCH\_2AF input on Hyundai/Kia/Genesis CAN-FD, validated for layout, checksum, counter and freshness without a vehicle-name whitelist, resets interaction timing while held when camera monitoring is unavailable; healthy-camera mode 1 counts only a new contact. Healthy-camera mode 0 stays stock. Shared exception: in both modes with or without a camera, one continuous second of valid Park, standstill and disengaged status resets accumulated warnings and lockout. Zero speed or engagement OFF/ON alone cannot release it; re-engagement is manual.

<!-- CARROT:AUTO:BEGIN DriverMonitoringMode -->
<!-- CARROT:AUTO:SOURCE facts="0c11a110afad8cda57907f9dca212f3cf242fb291e5bd7d9817f4d27b0222028" semantic="41de43ecd7b558bf3408066b776219f5a1367f4ed91a5aae8a31995a4f0b821a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Standard (`0`)
- **Range:** Standard (`0`) ~ Experimental (testing only) (`1`)
- **Step:** `1`
- **Options:** `0` Standard, `1` Experimental (testing only)
- **Menu:** Vehicle & Hardware \> Driver Monitor
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringMode -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringMode -->
<!-- CARROT:REVIEW reviewed-for="71597058dbc3a5673ec5c3fa80f182b7386309654371ebfdfcbf577dd83a765d" reviewed-at="2026-09-28T23:46:27.802775+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Standard mode retains comma behavior with a healthy camera and uses separate interaction timing when camera monitoring is unavailable. Experimental mode extends timing on an observed empty road, defers camera warnings after driver/BT input, and resets monitoring with confident forward attention.

Original STEER_TOUCH_2AF wheel touch on Hyundai/Kia/Genesis CAN-FD, validated for layout, checksum, counter and freshness without a vehicle-name whitelist, maintains the interaction timer while held when camera monitoring is unavailable. With a healthy camera, experimental mode counts only new contact after a valid release; holding or reconnecting does not repeatedly renew grace. Healthy-camera standard mode stays stock, and touch cannot clear terminal warnings.
Camera absence, startup preparation or failure silently selects interaction monitoring; two continuous seconds of healthy required inputs restore camera monitoring. Driver-unresponsive warnings and monitoring-process and vehicle-communication fault detection remain active.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use experimental mode only in controlled tests. Mode changes apply live at roughly half-second intervals without rebooting, preserving accumulated monitoring time, warning counts and lockout. Previous interaction grace and the forward-attention streak end. Only moving traffic appearing after an absence starts 20 seconds of standard monitoring. Additional or continuously observed vehicles do not extend it; experimental monitoring then resumes, without the empty-road bonus while traffic remains. A healthy camera uses stock detection and input handling during the hold, suspending experimental grace and special forward-attention resets. Previous grace ends; all observations must clear beyond their two-second retention before another appearance can trigger a hold.

In both modes with or without a camera, one continuous second of valid Park, standstill and disengaged status resets accumulated warnings and lockout. This exception also applies to standard mode; zero speed or engagement OFF/ON alone cannot release it, and re-engagement is manual.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Interaction grace also delays sleep, eye-closure and phone warnings; it does not guarantee wakefulness or legal compliance. See [four-mode timing, grace, resets and terminal limits](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/driver-monitoring.md).
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END DriverMonitoringMode -->

<!-- CARROT:SETTING:END DriverMonitoringMode -->
