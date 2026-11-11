<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_STOPGO" param="StoppingAccel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# StoppingStartAccelx0.01(-50)

**Menu:** Driving \> Cruise & Gap \> Stop & Resume

---

<!-- CARROT:SETTING:BEGIN StoppingAccel -->
<a id="StoppingAccel"></a>

## StoppingStartAccelx0.01(-50)

`StoppingAccel`

Adjust the stop-entry acceleration threshold and stopping target. Only -100 to -50 is allowed; -50 means -0.50 m/s². More negative values request stronger deceleration. Existing stronger braking is retained, and soft hold uses the vehicle-specific hold acceleration. Changes apply within about one second, including while driving. For Hyundai/Kia CANFD openpilot longitudinal control, aReqRaw and aReqValue become zero in the first StopReq frame, so this setting does not change transmitted acceleration while StopReq remains active. Automatic release/retry is removed.

<!-- CARROT:AUTO:BEGIN StoppingAccel -->
<!-- CARROT:AUTO:SOURCE facts="dda627c068e414ef029b768b503cebbe4b2df17300d23fcb41e1e7c2f6cdd83e" semantic="804fd76b953b107e414ad27b3ef47d2d75140f0fd06273972f700c8ec2f23490" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `-50`
- **Range:** `-100` ~ `-50`
- **Step:** `10`
- **Menu:** Driving \> Cruise & Gap \> Stop & Resume
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END StoppingAccel -->

<!-- CARROT:MANUAL:BEGIN StoppingAccel -->
<!-- CARROT:REVIEW reviewed-for="804fd76b953b107e414ad27b3ef47d2d75140f0fd06273972f700c8ec2f23490" reviewed-at="2026-10-10T09:34:33+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

**Raise it (less negative):** requests weaker deceleration and delays the ordinary acceleration-based handover to stopping.

**Lower it (more negative):** requests stronger deceleration and advances that handover, which can increase stopping impact. Existing stronger requests are retained; soft hold uses the vehicle-specific hold acceleration.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Changes apply within about one second, including while driving. Selecting a weaker target during an ongoing stop does not immediately reduce stronger output already reached.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

The stored value is multiplied by 0.01 to obtain m/s². Control also enforces the setting bounds. It does not directly apply to stock ACC longitudinal control; Hyundai/Kia CANFD sends both aReq fields as zero from the first StopReq frame, without automatic retry. This setting still affects stop entry but does not change final transmitted acceleration while StopReq remains active, including soft hold. See the [stop and resume guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/cruise-gap.md#stop-resume).
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END StoppingAccel -->

<!-- CARROT:SETTING:END StoppingAccel -->
