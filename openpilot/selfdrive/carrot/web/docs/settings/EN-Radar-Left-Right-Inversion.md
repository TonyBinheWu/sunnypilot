<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_RADAR" param="RadarTrackFlip" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Radar Left/Right Inversion

**Menu:** Vehicle & Hardware \> Radar

---

<!-- CARROT:SETTING:BEGIN RadarTrackFlip -->
<a id="RadarTrackFlip"></a>

## Radar Left/Right Inversion

`RadarTrackFlip`

Corrects the lateral orientation of front radar tracks. 0: Normal (default) 1: Invert lateral position and velocity Does not apply to SCC, corner radar or vision. Affects both lead selection and radar display. No vehicle is inverted automatically; select only after confirming a left/right mismatch. Restart the vehicle or reboot the device after changing this setting.

<!-- CARROT:AUTO:BEGIN RadarTrackFlip -->
<!-- CARROT:AUTO:SOURCE facts="28a45ebb8b39aa197418a029454638ae94e647b6218288adae8c31c6cb3c28dc" semantic="943dbe7612241b525566748d4a0c0383a19f20e4a140a100fad0a061f818df64" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Normal (`0`)
- **Range:** Normal (`0`) ~ Invert left/right (`1`)
- **Step:** `1`
- **Options:** `0` Normal, `1` Invert left/right
- **Menu:** Vehicle & Hardware \> Radar
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RadarTrackFlip -->

<!-- CARROT:MANUAL:BEGIN RadarTrackFlip -->
<!-- CARROT:REVIEW reviewed-for="bd236f17fd9177f84d830907b23c61d75e1e8216aac4ca4dfb3cc9e3d4460cb8" reviewed-at="2026-09-23T00:19:35.892356+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Normal preserves front-track coordinates; inversion reverses both lateral position and lateral velocity. It affects lead selection and radar display while preserving SCC, corner radar, vision and longitudinal distance/speed.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Select inversion only after confirming a left/right mismatch between video and radar. There is no automatic inversion by vehicle model; restart the vehicle or reboot the device to apply the change at the next OnRoad start.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END RadarTrackFlip -->

<!-- CARROT:SETTING:END RadarTrackFlip -->
