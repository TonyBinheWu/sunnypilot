<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_RADAR" param="EnableRadarTracks" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Enable radar tracks(0)

**Menu:** Vehicle & Hardware \> Radar

---

<!-- CARROT:SETTING:BEGIN EnableRadarTracks -->
<a id="EnableRadarTracks"></a>

## Enable radar tracks(0)

`EnableRadarTracks`

-2: VOACC vision-only test -1: Always use SCC without vision matching; vision if absent 0: Always use SCC range and relative speed; vision if absent 1: Match front radar without SCC; vision if it fails 2: Match front radar + low-speed SCC; vision if it fails 3: If front-radar vision matching fails, use SCC (not when front/corner radar place that body in another lane); vision if absent New vision requires prob \>= 0.40; all SCC association ignores lateral position Legacy Mando 32/64-slot variants are detected automatically

<!-- CARROT:AUTO:BEGIN EnableRadarTracks -->
<!-- CARROT:AUTO:SOURCE facts="0d5e1cdebc12922bf6a8ef02eebdd9de495b55302d6af450ec7937009f06f8be" semantic="0aab8f5fa0c29c37fd4b650cd2a25ffe0451f1c62b9f8fcbcb386721f8c81218" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `0`
- **Range:** `-2` ~ `3`
- **Step:** `1`
- **Menu:** Vehicle & Hardware \> Radar
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableRadarTracks -->

<!-- CARROT:MANUAL:BEGIN EnableRadarTracks -->
<!-- CARROT:REVIEW reviewed-for="0aab8f5fa0c29c37fd4b650cd2a25ffe0451f1c62b9f8fcbcb386721f8c81218" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value determines the L1 radar sources and vision matching policy.

- `-2` — Test vision-only control.
- `-1` — Use SCC without vision matching; use vision when SCC is absent.
- `0` — Always use SCC range and relative speed; use vision when SCC is absent.
- `1` — Match front radar without SCC to vision; use vision when matching fails.
- `2` — Match front radar and low-speed SCC to vision; use vision when matching fails.
- `3` — Use SCC after front-radar/vision matching fails, except when front/corner evidence places that body beside the path. Use vision when SCC is absent or rejected.

A new stationary front-radar object becomes L1 only after corresponding vision or a matching corner object confirms it. Long-range observation age and high track quality alone cannot authorize it; corner confirmation requires continuous agreement in range, lateral position, and speed.

When a separate measured moving target agrees with the visual position and speed, that vision cannot authorize or retain a different stationary reflection. A nearby high-quality stationary return needs its own matching corner evidence when its speed contradicts that moving vehicle. Corner confirmation belongs to the selected object itself. A front-only return whose range and speed both diverge from vision is released even when it is closer.

If an unconfirmed stationary front without corresponding corner corroboration loses visual support beyond the permitted 0.10-second hold, both its pending identity and confirmation start time reset. Renewed detection must complete three supported frames and a fresh 0.25-second confirmation; elapsed time from the interrupted detection is not reused.

For an already selected moving front vehicle, the range guard uses the model’s distance uncertainty instead of discarding radar solely because it is more than 8 m farther away. Both radar and vision must indicate motion above 4 m/s and remain central to the model path. The same front must stay measured and physically continuous, with no gap longer than 0.15 seconds. Its allowed farther-than-vision difference is `max(8 m, min(15 m, 15% of vision distance, 1.5 × xStd))`. Fresh IDs, missing matches, invalid paths, position or speed jumps, and precise nearer vision do not inherit that allowance. This adds no confirmation delay and does not prevent a better matching nearer front vehicle from becoming L1. A retained lead uses radar distance and speed; it does not average them with the visual estimates.

A distant stopped vehicle on a gentle curve can qualify through repeated visual position agreement while model velocity is still inaccurate. Beyond 60 m, the measured front must maintain position and speed continuity for at least 0.50 seconds, with `trackState >= 2`, `|vLead| <= 2 m/s`, `|dPath| <= 1.25 m`, and `|yawRate| < 0.10 rad/s`. At least two frames with vision probability 0.40 or higher must agree within 5 m in range and 1.25 m in raw lateral position; this recent position evidence expires after 0.50 seconds. Only this evidence plus sufficient visual-speed uncertainty permits disagreement within `min(24 m/s, 4 × vStd)`; a precise moving-speed estimate still rejects a stationary reflection. Fresh admission still requires current range agreement within 15 m, three supporting frames, and 0.25 seconds of confirmation. Radar ID age or the mere presence of a corner point is insufficient. A separately identified moving front/SCC retains the immediate veto. To contradict a front with this position history, the same corner must agree with visual position and speed while moving continuously for at least 0.15 seconds. Physically matching front/corner pairs retain their independent corroboration.

A confirmed stopped front can bridge brief visual-range noise while it remains measured and physically continuous, within `|dPath| <= 1.5 m` and 2 m of visual lateral position. Its farther-than-vision allowance is `max(8 m, min(25 m, 25% of vision distance, 2 × xStd))`. The allowance lasts at most 0.50 seconds after range agreement within 8 m or repeated position confirmation. Observation gaps over 0.15 seconds and position/speed jumps reset that history. An unconfirmed new object or a precise nearer visual estimate receives no such allowance. The lead continues to publish current radar distance and speed. These rules do not guarantee 100 m acquisition or zero false detections on every road.
In modes `EnableRadarTracks=1`–`3`, a confirmed departing front lead can receive bounded future headway relief in ACC when outward radar motion and a visual switch to a farther vehicle agree. See [predicted CUT-OUT behavior](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/radar.md).

Mode 3 bridges missing lateral support for at most one second. Range/speed discontinuities, missing SCC or path, and leaving the mode reset the previous refusal; a reused ID alone does not transfer it to another car.

With standard, unmodified HDA2 wiring and openpilot longitudinal control, startup disables the factory SCC transmitter while raw front radar remains a separate input. Missing factory SCC does not invalidate healthy raw tracks in this configuration; missing required raw frames still causes a fault. Camera-SCC wiring and passive Bosch reception retain their native SCC handling. Mode `1` matches front radar to vision; modes `2` and `3` have no SCC fallback when that transmitter is disabled. Restart after changing radar source or wiring settings. This does not enable corner radar.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On a supported radar configuration, change one item at a time and verify detection and tracking under the same lead and cut-in conditions.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> Physical radar presence alone does not prove support. Verify message reception and tracking on the same vehicle configuration.
<!-- CARROT:NOTICE:END -->

[Related user guide](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/en/radar.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END EnableRadarTracks -->

<!-- CARROT:SETTING:END EnableRadarTracks -->
