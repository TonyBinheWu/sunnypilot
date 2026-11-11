<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_CAMERA" param="AutoNaviCountDownMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NaviCountDownMode

**Menu:** Driving \> Speed & Decel \> Speed Camera

---

<!-- CARROT:SETTING:BEGIN AutoNaviCountDownMode -->
<a id="AutoNaviCountDownMode"></a>

## NaviCountDownMode

`AutoNaviCountDownMode`

Uses only external-navigation distances while connected, and stock-navigation distances otherwise. Changing the connection state resets the previous countdown. 0:not use, 1: turn point + speed, 2: turn point + speed + bump

<!-- CARROT:AUTO:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:AUTO:SOURCE facts="0226a6962074019817aa7aabdca880556f39740be5ccd79cf8fbc29dd70ac54d" semantic="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `2`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Speed & Decel \> Speed Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviCountDownMode -->

<!-- CARROT:MANUAL:BEGIN AutoNaviCountDownMode -->
<!-- CARROT:REVIEW reviewed-for="164adc98b3573e2f4d0ea6aa380a9920ed4d56a1dc37b6bdf056a7ae5f0de063" reviewed-at="2026-09-13T07:52:39.752117+00:00" -->

<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

While external navigation is connected, it is used exclusively even without a current guidance item. After disconnection or receive timeout is detected, stock navigation resumes according to its settings.

0 disables alerts; 1 includes turn points and speed events; 2 also includes bumps. Only external distances are used while connected and stock distances otherwise. Changing the connection state resets the previous countdown. This does not change deceleration timing or strength.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check the external-navigation connection together with the displayed event type and remaining distance.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoNaviCountDownMode -->

<!-- CARROT:SETTING:END AutoNaviCountDownMode -->
