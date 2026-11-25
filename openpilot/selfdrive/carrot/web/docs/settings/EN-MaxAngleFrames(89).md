<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_AUX" param="MaxAngleFrames" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# MaxAngleFrames(89)

**Menu:** Vehicle & Hardware \> Vehicle Aux

---

<!-- CARROT:SETTING:BEGIN MaxAngleFrames -->
<a id="MaxAngleFrames"></a>

## MaxAngleFrames(89)

`MaxAngleFrames`

Recommended setting: 89. On the 2024 Sorento with camera SCC and torque steering, the controller uses 92–94 frames to match the camera cadence. EV6 HDA2 torque steering on the ADAS ECU uses a fixed 89 request frames followed by 2 cut frames while wheel angle stays at or beyond 85 degrees in either direction.

<!-- CARROT:AUTO:BEGIN MaxAngleFrames -->
<!-- CARROT:AUTO:SOURCE facts="041f33ed4775420de9e45de190bd998e88fc5d0972f9a9488272422d9576138e" semantic="3efcdf66d1890c952d559944a1833a717b8b8cec62bcdab5fed66cd6ea160801" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `89`
- **Range:** `89` ~ `100`
- **Step:** `1`
- **Menu:** Vehicle & Hardware \> Vehicle Aux
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MaxAngleFrames -->

<!-- CARROT:MANUAL:BEGIN MaxAngleFrames -->
<!-- CARROT:REVIEW reviewed-for="c21f5b2f6d919fcc7d07af6ad5fe3f43c01fc42b1a190dd097bbd44f74ebad29" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Adjusts how many consecutive steering-request frames are allowed at large steering angles.

- **Higher:** Allows steering requests for more frames at large steering angles.
- **Lower:** Stops the request earlier to avoid an EPS fault.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time only on supported vehicles, then verify steering or stock SCC behavior on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> A value that does not match the vehicle control configuration can change steering or stock-SCC behavior.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MaxAngleFrames -->

<!-- CARROT:SETTING:END MaxAngleFrames -->
