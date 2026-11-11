<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleSpeedCameraDistanceTime" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Vehicle Speed Camera Virtual Distance Time (6.0 s)

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleSpeedCameraDistanceTime -->
<a id="VehicleSpeedCameraDistanceTime"></a>

## Vehicle Speed Camera Virtual Distance Time (6.0 s)

`VehicleSpeedCameraDistanceTime`

Applies only when external navigation is disconnected. While external navigation is connected, stock navigation is excluded even without a current guidance item. Creates a virtual deceleration distance when the vehicle sends only a speed-camera enforcement speed without distance. The stored value uses 0.1-second units: 60 means 6.0 s and 62 means 6.2 s. Virtual distance (m) = enforcement speed (km/h) × configured time (s), so 62 produces 310 m at 50 km/h. A smaller value shortens the virtual distance, so deceleration may begin earlier or more strongly. Changes take effect within about one second while driving. Also applies on supported CAN-FD vehicles when no nearby distance matches the current warning. A new warning or limit change restarts the distance; once exhausted, the cap remains while the warning is active without repeatedly extending the virtual distance.

<!-- CARROT:AUTO:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:AUTO:SOURCE facts="ba9080bab8f245fcb2574d2adb825ce78207386f3f0f7804f6b08f0c1fdf8843" semantic="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `60`
- **Range:** `10` ~ `200`
- **Step:** `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:MANUAL:BEGIN VehicleSpeedCameraDistanceTime -->
<!-- CARROT:REVIEW reviewed-for="b3ca6436f7051d2fd82ae24a9dc3974abf6b5ee32c633d085c3eb4bee630c364" reviewed-at="2026-09-13T09:14:58.915692+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

While external navigation is connected, it is used exclusively even without a current guidance item. After disconnection or receive timeout is detected, stock navigation resumes according to its settings.

Computes a virtual distance when the vehicle supplies an enforcement speed without distance. Increasing the value lengthens that distance; decreasing it shortens the distance and can start deceleration earlier or more strongly.
On supported CAN-FD vehicles, this also applies when no nearby distance matches the current warning. A new warning or limit change starts a fresh distance, which decreases with travel. Once exhausted, the cap remains while the warning is active without repeatedly extending the virtual distance.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the external-navigation connection together with the displayed event type and remaining distance.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleSpeedCameraDistanceTime -->

<!-- CARROT:SETTING:END VehicleSpeedCameraDistanceTime -->
