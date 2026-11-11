<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="LeadAccelResponseTF1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF1 following responsiveness

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponseTF1 -->
<a id="LeadAccelResponseTF1"></a>

## TF1 following responsiveness

`LeadAccelResponseTF1`

Following responsiveness at cruise gap 1. -1 uses the common setting; 0–5 overrides it for this gap. Gaps may share the same base TF with different responses. After resolving the common or gap-specific choice, Eco applies at most 2 and Safe at most 3. Normal and High retain the selected value. Lower values and 0 are never raised; stored settings are unchanged. Extra-headroom hold conditions apply up to 1.2 times TF distance (speed × TF + stopping distance), ease progressively from 1.2 to 1.5 times, and no longer pause recovery at or above 1.5 times regardless of lead speed. Braking-onset distance is not separately remembered or held after stopping.

<!-- CARROT:AUTO:BEGIN LeadAccelResponseTF1 -->
<!-- CARROT:AUTO:SOURCE facts="4c151b7d1a39e84894d25b2dec96d8907c6ba31acc034cc2acfb72f67879b3e0" semantic="095edb40730e0a41998e0ade9729636a60de3f36b5e93f22b4eaf6a85acb84f3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Use common (`-1`)
- **Range:** Use common (`-1`) ~ 5 Maximum follow (test) (`5`)
- **Step:** `1`
- **Options:** `-1` Use common, `0` 0 Relaxed recovery, `1` 1 Most gradual, `2` 2 Gentle follow, `3` 3 Balanced follow, `4` 4 Urgent follow, `5` 5 Maximum follow (test)
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponseTF1 -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponseTF1 -->
<!-- CARROT:REVIEW reviewed-for="92118c8853805bdcfe52a1837ccd9c3dd6925e1d8ee95a39b9ae408011a0f056" reviewed-at="2026-10-05T01:00:23.766230+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Cruise gap 1 uses either the common response or its selected override. Higher levels follow faster; lower levels recover the gap more gradually.

After resolving the common or gap-specific response, Eco caps it at 2 and Safe at 3. Normal and High retain the selected value; lower choices and 0 are never raised, and stored values are unchanged.

Additional headroom at levels 0–4 has a distance-limited hold. Reference D is speed × base TF + configured stopping distance, excluding extra headroom.

- Up to 1.2D: existing hold/recovery conditions apply.
- From 1.2D to 1.5D: the retained envelope and replenishment rate decrease while low-speed recovery restrictions ease.
- At or above 1.5D: recover at the selected level’s rate even for a pulling-away or stopped lead.

This does not erase the allowance instantly or directly add acceleration. Base TF, stopping distance, braking constraints and level 5’s absence of extra headroom remain unchanged.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Two gaps may use the same base TF with different responses. The selected response controls acceleration boost and extra-headroom recovery while retaining speed TF.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponseTF1 -->

<!-- CARROT:SETTING:END LeadAccelResponseTF1 -->
