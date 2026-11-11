<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="LeadAccelResponseTF4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF4 following responsiveness

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponseTF4 -->
<a id="LeadAccelResponseTF4"></a>

## TF4 following responsiveness

`LeadAccelResponseTF4`

Following responsiveness at cruise gap 4. -1 uses the common setting; 0–5 overrides it for this gap. Gaps may share the same base TF with different responses. After resolving the common or gap-specific choice, Eco applies at most 2 and Safe at most 3. Normal and High retain the selected value. Lower values and 0 are never raised; stored settings are unchanged. Extra-headroom hold conditions apply up to 1.2 times TF distance (speed × TF + stopping distance), ease progressively from 1.2 to 1.5 times, and no longer pause recovery at or above 1.5 times regardless of lead speed. Braking-onset distance is not separately remembered or held after stopping.

<!-- CARROT:AUTO:BEGIN LeadAccelResponseTF4 -->
<!-- CARROT:AUTO:SOURCE facts="d17f019e39b7bfa66e6422f818788b3c2c7528be124f213b5c67fe0a7620bf92" semantic="98a6de3affc56a6d1146a72fe4af4fe954aaf9bca912ea89256434a150b6a595" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** Use common (`-1`)
- **Range:** Use common (`-1`) ~ 5 Maximum follow (test) (`5`)
- **Step:** `1`
- **Options:** `-1` Use common, `0` 0 Relaxed recovery, `1` 1 Most gradual, `2` 2 Gentle follow, `3` 3 Balanced follow, `4` 4 Urgent follow, `5` 5 Maximum follow (test)
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponseTF4 -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponseTF4 -->
<!-- CARROT:REVIEW reviewed-for="86649c8bc61cf3c79e9166987b9b53dcf40b9e0456bbfdf0e5093eb888a42174" reviewed-at="2026-10-05T01:00:23.770237+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Cruise gap 4 uses either the common response or its selected override. Higher levels follow faster; lower levels recover the gap more gradually.

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

<!-- CARROT:MANUAL:END LeadAccelResponseTF4 -->

<!-- CARROT:SETTING:END LeadAccelResponseTF4 -->
