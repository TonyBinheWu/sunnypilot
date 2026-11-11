<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="LaneChangeLeverWait" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# One-touch lane change request waits 5 flashes

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN LaneChangeLeverWait -->
<a id="LaneChangeLeverWait"></a>

## One-touch lane change request waits 5 flashes

`LaneChangeLeverWait`

Hyundai CAN-FD only (0x3C1 lever signal). When a one-touch lever press is not approved at once (BSD, side vehicle, lane lines: the existing checks), the turn signal is held and the request waits for 5 flashes (about 4 s) from the press. If it clears in time the lane change starts; otherwise the request is dropped and the remaining flashes do not start it. A latched lever keeps waiting as before.

<!-- CARROT:AUTO:BEGIN LaneChangeLeverWait -->
<!-- CARROT:AUTO:SOURCE facts="a9789852f0269882642c9dfbf052db7270060c161960cda67ef9ce2817a159fb" semantic="ea223332818ad995bfa4b772614a0e20f4c64f676f70ec1be8afd5eb871ae2db" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LaneChangeLeverWait -->

<!-- CARROT:MANUAL:BEGIN LaneChangeLeverWait -->
<!-- CARROT:REVIEW reviewed-for="ea223332818ad995bfa4b772614a0e20f4c64f676f70ec1be8afd5eb871ae2db" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

When enabled, a one-touch lane-change request blocked by BSD or lane checks holds the signal and request for about four seconds, plus the configured entry delay. It then expires. When disabled, existing lamp-based waiting applies.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

A latched lever continues waiting under the existing checks. Make a new request after a timed request expires.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END LaneChangeLeverWait -->

<!-- CARROT:SETTING:END LaneChangeLeverWait -->
