<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_LANECHANGE" param="ManualLaneChangeIndicator" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Manual lane-change indicator (trial)

**Menu:** Driving \> Steering \> Lane Change (Auto Turn)

---

<!-- CARROT:SETTING:BEGIN ManualLaneChangeIndicator -->
<a id="ManualLaneChangeIndicator"></a>

## Manual lane-change indicator (trial)

`ManualLaneChangeIndicator`

At 5km/h or above, same-direction steering is confirmed for 0.15s. Release or brief countersteer does not erase continued boundary approach: recent intent is retained for up to 1.5s. Approach stopping for over 0.3s, retreat exceeding 0.15m or a four-second episode limit cancels tracking. On the left, fresh OEM white-line classification excludes centre lines; yellow, unknown or stale classifications block requests. On the right, road-edge clearance beyond the approached boundary must be at least 2.5m both nearby and ahead. Outer-line probability, adjacent lane width and road-edge standard deviation are not admission conditions. A wide shoulder can also pass the distance condition. Independent of ATC and the right-turn distance option; never requests automatic steering. Default OFF; Ioniq 5 PE with Jetson USB2CAN and AutoBlinkerControl 1 or 2 only. New requests need three seconds and one second of lamp extinction; steering-feedback isolation remains at least 12 seconds. Detection does not guarantee a real lane or safe gap. Revised behavior needs physical validation. Entry anchors target-line confidence of at least 10%; continuous approach may then be tracked for up to four seconds. After requesting, tracks completion, return or invalid inputs for at most 12 seconds. Immediate extinction of OEM one-touch flashing is not guaranteed. Measured boundary approach projects 0.3 seconds ahead to request indication earlier. The centre-to-boundary distance threshold advances from 0.9m to at most 1.2m; at least 0.15m of actual approach, driver intent and consistent movement of both boundaries remain required.

<!-- CARROT:AUTO:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:AUTO:SOURCE facts="7b315dcbb2763355a1fce447c7264783da61d5627b911238bc0678a32f72329d" semantic="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Lane Change (Auto Turn)
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ManualLaneChangeIndicator -->

<!-- CARROT:MANUAL:BEGIN ManualLaneChangeIndicator -->
<!-- CARROT:REVIEW reviewed-for="e2259bfc81f439587e99cd8f87f9640f16cb2ddb370571afbfd23611dc2f1d7f" reviewed-at="2026-11-08T22:13:25+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Indicates recent driver intent with continuous boundary approach. Entry anchors target-line confidence of at least 10% and applies left centre-line and right road-edge exclusions.

After a request it tracks completion, return and invalid inputs without requesting automatic steering. OEM one-touch flashing may remain after the hold ends.
Measured boundary approach projects 0.3 seconds ahead to request indication earlier. The centre-to-boundary distance threshold advances from 0.9m to at most 1.2m; at least 0.15m of actual approach, driver intent and consistent movement of both boundaries remain required.

Manual/model indication distinguishes its short one-touch echo only with matching request time, direction and stalk counters. Opposite input, a latched lever or receiver-detected driver intervention cancels. Lamp feedback preceding the completed-send response is remembered briefly; holding still requires the matching response. Same-direction physical input during the brief transmission interval cannot be uniquely distinguished from these fields alone.
From 5 km/h, manual steering and measured approach to an adjacent lane can trigger the corresponding indicator.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END ManualLaneChangeIndicator -->

<!-- CARROT:SETTING:END ManualLaneChangeIndicator -->
