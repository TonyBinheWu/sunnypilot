<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviCanControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Vehicle Navigation CAN Deceleration Mode

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviCanControl -->
<a id="VehicleNaviCanControl"></a>

## Vehicle Navigation CAN Deceleration Mode

`VehicleNaviCanControl`

Applies only when external navigation is disconnected. While external navigation is connected, stock navigation is excluded even without a current guidance item. Select when exact stock-navigation CAN camera and bump distances are used for deceleration. Route match means the vNAVI future event matches the currently calculated route and path. 0: Disabled 1: Always use cameras and bumps 2: Always use cameras; use bumps only on the calculated route 3: Use cameras and bumps only on the calculated route Route data older than two seconds is treated as no route. Current camera states confirmed directly by the vehicle are controlled separately by VehicleSpeedCameraControlMode. A directly confirmed PV5 section remains active in modes 1–3. Experimental; use only on a validated vehicle. A current camera warning uses only a nearby distance candidate with the same limit; if only a distant same-speed camera exists, it uses the current warning's own virtual distance.

<!-- CARROT:AUTO:BEGIN VehicleNaviCanControl -->
<!-- CARROT:AUTO:SOURCE facts="7705af34e08985f694042118b413cff9a8b672255c2d74caf1366bc576227795" semantic="f8d1712821a73e6fe7eba60cf61124d25e39d1cbafcd0c3129f9732ab42f4b13" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Disabled (`0`)
- **Range:** Disabled (`0`) ~ Camera & bump on route (`3`)
- **Step:** `1`
- **Options:** `0` Disabled, `1` Always camera & bump, `2` Camera always, bump on route, `3` Camera & bump on route
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviCanControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviCanControl -->
<!-- CARROT:REVIEW reviewed-for="9598e2a6ce6b00dcd5e8a0f1feae8f420e87990f1a27edc0aa0a46bbff15d34b" reviewed-at="2026-09-13T09:14:58.908692+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

While external navigation is connected, it is used exclusively even without a current guidance item. After disconnection or receive timeout is detected, stock navigation resumes according to its settings.

Without external navigation, 0 disables this control; 1 uses cameras and bumps regardless of route guidance; 2 always uses cameras and requires a route match for bumps; 3 requires a route match for both. Directly confirmed current camera states follow the vehicle-received camera control setting.
A current camera warning is associated only with a nearby distance with the same limit. If only a distant same-speed camera exists, the current warning uses its own virtual distance while the distant camera remains queued for a later approach.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the external-navigation connection together with the displayed event type and remaining distance.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviCanControl -->

<!-- CARROT:SETTING:END VehicleNaviCanControl -->
