<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CURVE" param="AutoCurveSpeedFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# CurveSpeedFactor(100%)

**Menu:** Driving \> Speed & Decel \> Curve & Turn

---

<!-- CARROT:SETTING:BEGIN AutoCurveSpeedFactor -->
<a id="AutoCurveSpeedFactor"></a>

## CurveSpeedFactor(100%)

`AutoCurveSpeedFactor`

Higher values lower the lateral-acceleration budget and curve target speed. Slowing starts according to the distance to the curve.

<!-- CARROT:AUTO:BEGIN AutoCurveSpeedFactor -->
<!-- CARROT:AUTO:SOURCE facts="6a40e20d0d3b6186bff96606a8e0d429467a99c243be5724a78643dcd3b65016" semantic="93b019e883847557a9ef42b96bfac26369726ea7c3b0b3c5155e8e10658ac930" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100%`
- **Range:** `50%` ~ `300%`
- **Step:** `5`
- **Display unit:** `%`
- **Menu:** Driving \> Speed & Decel \> Curve & Turn
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoCurveSpeedFactor -->

<!-- CARROT:MANUAL:BEGIN AutoCurveSpeedFactor -->
<!-- CARROT:REVIEW reviewed-for="93b019e883847557a9ef42b96bfac26369726ea7c3b0b3c5155e8e10658ac930" reviewed-at="2026-09-18T11:24:20+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Curvature comes from yaw rate and velocity at the same predicted point. The setting divides the lateral-acceleration budget to set a curve target; remaining distance, control response and gradual braking determine the current approach ceiling.

- **Higher:** Lowers the target speed for the same curve.
- **Lower:** Raises the target speed for the same curve.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Adjust one item at a time while comparing the target before entry and speed through the same curve.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Distant predicted velocity is not used directly as a driving-speed target. Late predictions can still delay slowing.

When consecutive fresh model paths confirm that the turn is easing, vTurn recovers promptly to the lowest ceiling from roughly the last 0.25 seconds. A tighter curve limit applies immediately; repeated frames or missing model input do not justify fast release.

Actual acceleration still follows the existing acceleration and jerk limits.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoCurveSpeedFactor -->

<!-- CARROT:SETTING:END AutoCurveSpeedFactor -->
