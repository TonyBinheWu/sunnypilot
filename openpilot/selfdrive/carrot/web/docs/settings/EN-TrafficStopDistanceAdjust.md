<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_TRAFFIC" param="TrafficStopDistanceAdjust" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TrafficStopDistanceAdjust

**Menu:** Driving \> Speed & Decel \> Traffic Light

---

<!-- CARROT:SETTING:BEGIN TrafficStopDistanceAdjust -->
<a id="TrafficStopDistanceAdjust"></a>

## TrafficStopDistanceAdjust

`TrafficStopDistanceAdjust`

Adjusts signal-stop position. A confirmed stationary vehicle just ahead of the stop endpoint is corrected automatically to vehicle-relative spacing.

<!-- CARROT:AUTO:BEGIN TrafficStopDistanceAdjust -->
<!-- CARROT:AUTO:SOURCE facts="a7320536f231c217ec95f4d80b0474e86d0a4765f3d1438b464fcd8fe3957bf9" semantic="2c0307757de5931be931759240b41c4dbfa911d065c2e58f09356222e3b41eaa" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `-150cm`
- **Range:** `-600cm` ~ `600cm`
- **Step:** `100`
- **Display unit:** `cm`
- **Menu:** Driving \> Speed & Decel \> Traffic Light
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TrafficStopDistanceAdjust -->

<!-- CARROT:MANUAL:BEGIN TrafficStopDistanceAdjust -->
<!-- CARROT:REVIEW reviewed-for="97928b4e4d95a660327b16834bf290d7c92ac14c300939e11ba569c177f25244" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Adds a distance correction to the virtual traffic-signal stop obstacle while the vehicle is moving.

- **Positive:** Moves the stop target farther forward along the road.
- **Negative:** Pulls the stop target toward the vehicle.

While stopped, the current code uses a separate `-2 m` correction.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

At the same clearly visible intersection, verify detection, stopping, restart timing, and stop position.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TrafficStopDistanceAdjust -->

<!-- CARROT:SETTING:END TrafficStopDistanceAdjust -->
