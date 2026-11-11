<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_TRAFFIC" param="TrafficLightDetectMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TrafficLightDetectMode

**Menu:** Driving \> Speed & Decel \> Traffic Light

---

<!-- CARROT:SETTING:BEGIN TrafficLightDetectMode -->
<a id="TrafficLightDetectMode"></a>

## TrafficLightDetectMode

`TrafficLightDetectMode`

0:None,1:Stopping only, 2:Stop & Go

<!-- CARROT:AUTO:BEGIN TrafficLightDetectMode -->
<!-- CARROT:AUTO:SOURCE facts="1d1fb189ed216e0fc84c6eb24bfde3a977c7498addc53b2a7ef171dce6f45993" semantic="fd5f942d148667ec255b07cf1ad246adcea8b41be25a134af644d9c7d0792e99" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `2`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Speed & Decel \> Traffic Light
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TrafficLightDetectMode -->

<!-- CARROT:MANUAL:BEGIN TrafficLightDetectMode -->
<!-- CARROT:REVIEW reviewed-for="fd5f942d148667ec255b07cf1ad246adcea8b41be25a134af644d9c7d0792e99" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — None
- `1` — Stopping only
- `2` — Stop & Go
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

At the same clearly visible intersection, verify detection, stopping, restart timing, and stop position.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Traffic-light detection is an assistance feature; the driver must verify the actual signal and traffic situation.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TrafficLightDetectMode -->

<!-- CARROT:SETTING:END TrafficLightDetectMode -->
