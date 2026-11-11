<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_BUMP" param="AutoNaviSpeedBumpEndDistance" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Speed Bump Early Release Distance (200 cm)

**Menu:** Driving \> Speed & Decel \> Speed Bump

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedBumpEndDistance -->
<a id="AutoNaviSpeedBumpEndDistance"></a>

## Speed Bump Early Release Distance (200 cm)

`AutoNaviSpeedBumpEndDistance`

While external navigation is connected, release uses only its remaining distance; otherwise it uses stock-navigation distance. Release the speed-bump deceleration limit when the remaining distance from stock navigation or Carrot Navi is at or below this value. The stored and displayed unit is cm; 0 keeps control until the received point. This compensates when the mapped bump lies behind the physical bump and speed recovery otherwise starts late. Setting it too high can allow acceleration before the actual bump.

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedBumpEndDistance -->
<!-- CARROT:AUTO:SOURCE facts="f99635c40ccfffe7b0bbeeccfc73214a4b17c4e42c22225668dce7bf039ee76f" semantic="1d2c29dce19e2a3851161d46ce76db89eb7be23e3f9b3b3c1be663a3e2b402c9" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `200cm`
- **Range:** `0cm` ~ `5000cm`
- **Step:** `10`
- **Display unit:** `cm`
- **Menu:** Driving \> Speed & Decel \> Speed Bump
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedBumpEndDistance -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedBumpEndDistance -->
<!-- CARROT:REVIEW reviewed-for="1d2c29dce19e2a3851161d46ce76db89eb7be23e3f9b3b3c1be663a3e2b402c9" reviewed-at="2026-09-13T07:52:39.852612+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

While external navigation is connected, it is used exclusively even without a current guidance item. After disconnection or receive timeout is detected, stock navigation resumes according to its settings.

Increasing a positive value releases the bump cap with more distance remaining; decreasing it releases closer to the bump. Zero keeps the cap until no distance remains. While external navigation is connected, only its distance determines release. Release does not mean the original cruise speed is reached immediately.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the external-navigation connection together with the displayed event type and remaining distance.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedBumpEndDistance -->

<!-- CARROT:SETTING:END AutoNaviSpeedBumpEndDistance -->
