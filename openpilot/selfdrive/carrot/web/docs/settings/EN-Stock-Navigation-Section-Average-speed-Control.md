<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="VehicleNaviSectionAvgControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Stock Navigation Section Average-speed Control

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN VehicleNaviSectionAvgControl -->
<a id="VehicleNaviSectionAvgControl"></a>

## Stock Navigation Section Average-speed Control

`VehicleNaviSectionAvgControl`

Applies only when external navigation is disconnected. A stock-navigation CAN section stays capped at its limit (x safety factor) as before. While engaged and with the cruise set speed above that cap, one press of cruise + or a gas tap unlocks the section: up to the set speed is then allowed only while the average since entering the section stays at or below the section limit. Only time banked by driving slower (e.g. congestion) can be spent; without it the cap is unchanged. The input does not raise the set speed. A long press of cruise - locks the section again without changing the set speed (a short press still lowers it as usual), and leaving the section resets it. The end camera still decelerates to the spot limit after its preview about 2 km ahead. The section start is taken when the average-speed signal appears; experimental.

<!-- CARROT:AUTO:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:AUTO:SOURCE facts="c3e6b77ef9dee82d4fd0755f82843209d501bbbf3aec480c3b3a757bd333efcc" semantic="279eeacf277d306a733765fc4b26354220278af698c6266e606d727260d2e3ec" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviSectionAvgControl -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviSectionAvgControl -->
<!-- CARROT:REVIEW reviewed-for="279eeacf277d306a733765fc4b26354220278af698c6266e606d727260d2e3ec" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Even when enabled, entering a section retains the existing limit cap. While engaged with a higher set speed, + or a gas tap unlocks speed up to the set speed using time banked by slower travel. Disabling retains the existing section cap.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Applies without external navigation. Hold - to lock again; leaving the section resets it. This experimental estimate depends on the entry signal and travelled distance. End-camera spot deceleration remains active.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviSectionAvgControl -->

<!-- CARROT:SETTING:END VehicleNaviSectionAvgControl -->
