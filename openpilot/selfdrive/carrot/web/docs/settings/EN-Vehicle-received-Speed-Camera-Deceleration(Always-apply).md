<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleSpeedCameraControlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Vehicle-received Speed Camera Deceleration(Always apply)

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraControlMode -->
<a id="VehicleSpeedCameraControlMode"></a>

## Vehicle-received Speed Camera Deceleration(Always apply)

`VehicleSpeedCameraControlMode`

Applies only when external navigation is disconnected. While external navigation is connected, stock navigation is excluded even without a current guidance item. Select how speed-camera enforcement speeds received over vehicle CAN are used for automatic deceleration. This does not affect speed-camera information received from Carrot Navi. 0: Disabled 1: Always apply regardless of accelerator input 2: Once vehicle-received camera deceleration has begun, a new accelerator press overrides the current event and keeps the highest speed reached during the override as its lower bound 3: Suspend vehicle-received speed-camera deceleration while the accelerator is pressed

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:AUTO:SOURCE facts="adb48a0a1a4f609f7ae9f213565ad0f2723cc8a40be1ada8a446a72226c81769" semantic="751d90cd219472ee82418f090d5685fd521295720a7ff37eb36bf0b66f9d92e9" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Always apply (`1`)
- **Range:** Disabled (`0`) ~ Suspend while accelerating (`3`)
- **Step:** `1`
- **Options:** `0` Disabled, `1` Always apply, `2` Accelerator decel override, `3` Suspend while accelerating
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraControlMode -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraControlMode -->
<!-- CARROT:REVIEW reviewed-for="9b48b9341a4ad5213f5220c933fa0f581110bf68f4e799917977eb831c1e67bd" reviewed-at="2026-09-13T07:52:39.940139+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

While external navigation is connected, it is used exclusively even without a current guidance item. After disconnection or receive timeout is detected, stock navigation resumes according to its settings.

0 disables control; 1 applies regardless of accelerator input; 2 retains the peak speed reached with a new accelerator press after deceleration starts until the event ends; 3 releases control while the accelerator is pressed. This mode does not control external-navigation deceleration.

On the Kia PV5, a matched camera distance remains active through brief notification pulses only while fresh stock-navigation messages continue to report the same enforcement limit. When enforcement ends, the limit changes, or either message is lost for more than one second, the current and queued camera distances are cleared.

A queued distance alone cannot trigger deceleration, including after the current camera's distance is exhausted. A new valid warning without a newly received matching distance uses the virtual distance below; an unchanged warning for a completed camera cannot restart it. PV5 route departure is not detected independently: cancellation relies on stock navigation ending or changing its enforcement state.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the external-navigation connection together with the displayed event type and remaining distance.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraControlMode -->

<!-- CARROT:SETTING:END VehicleSpeedCameraControlMode -->
