<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="DynamicTFollowLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Lane Change Response (100%)

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN DynamicTFollowLC -->
<a id="DynamicTFollowLC"></a>

## Lane Change Response (100%)

`DynamicTFollowLC`

Keeps base TF and allows bounded relief only after confirmed departure and sufficient spacing of normally selected leads. The normally selected leadOne/leadTwo at lane-change entry form the reference pair. If either selected lead changes or disappears, additional acceleration relief stops for the rest of that maneuver. Braking uses only the currently selected leads; side radar candidates and stored entry vehicles never become additional braking obstacles. 100 disables relief; lower values increase it, with the same cap at 80 and below. Maximum relief is 0.25 seconds and 4 metres.

<!-- CARROT:AUTO:BEGIN DynamicTFollowLC -->
<!-- CARROT:AUTO:SOURCE facts="af67289372b58e262ede3c58c5681dc25db111c865765f6268da503dc4356b44" semantic="50c56f4f2de5df94d98f4e119aa5b15e7798602f30b9dfa55b943d4e48280693" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `100%`
- **Range:** `20%` ~ `100%`
- **Step:** `5`
- **Display unit:** `%`
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DynamicTFollowLC -->

<!-- CARROT:MANUAL:BEGIN DynamicTFollowLC -->
<!-- CARROT:REVIEW reviewed-for="50c56f4f2de5df94d98f4e119aa5b15e7798602f30b9dfa55b943d4e48280693" reviewed-at="2026-09-09T03:21:39.035344+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The normally selected leadOne/leadTwo at lane-change entry form the reference pair. If either selected lead changes or disappears, additional acceleration relief stops for the rest of that maneuver. Braking uses only the currently selected leads; side radar candidates and stored entry vehicles never become additional braking obstacles.

Higher values reduce additional relief and the maximum disables it. Lower values increase confirmed post-clearance relief within the existing cap.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Check behavior at the default. Missing normally selected second-lead or pose information prevents additional relief.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:MANUAL:END DynamicTFollowLC -->

<!-- CARROT:SETTING:END DynamicTFollowLC -->
