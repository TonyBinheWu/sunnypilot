<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="LeadAccelResponse" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Following responsiveness · common

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponse -->
<a id="LeadAccelResponse"></a>

## Following responsiveness · common

`LeadAccelResponse`

Used when a gap response is set to Use common. Lower levels follow more gradually; higher levels respond faster. 0 disables acceleration boost; 5 is maximum response. Speed TF applies at every response level. After resolving the common or gap-specific choice, Eco applies at most 2 and Safe at most 3. Normal and High retain the selected value. Lower values and 0 are never raised; stored settings are unchanged. Extra-headroom hold conditions apply up to 1.2 times TF distance (speed × TF + stopping distance), ease progressively from 1.2 to 1.5 times, and no longer pause recovery at or above 1.5 times regardless of lead speed. Braking-onset distance is not separately remembered or held after stopping.

<!-- CARROT:AUTO:BEGIN LeadAccelResponse -->
<!-- CARROT:AUTO:SOURCE facts="595fcaa546a801b8c55a22e34bbf685c952dae5744b65748b5e8f7b7b00fb922" semantic="46d9ff7041e6f7680369b13cd90e72cfa05423b6ad5dbae8d537cadcb8858d89" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** 0 Relaxed recovery (`0`)
- **Range:** 0 Relaxed recovery (`0`) ~ 5 Maximum follow (test) (`5`)
- **Step:** `1`
- **Options:** `0` 0 Relaxed recovery, `1` 1 Most gradual, `2` 2 Gentle follow, `3` 3 Balanced follow, `4` 4 Urgent follow, `5` 5 Maximum follow (test)
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponse -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponse -->
<!-- CARROT:REVIEW reviewed-for="c487c8bba8fd571071a19fdbed3ea96f03f2b4dcf735b9e796ae232b73870670" reviewed-at="2026-10-11T08:11:40.285060+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Applies to cruise gaps set to Use common. Lower levels recover spacing more gradually; higher levels follow faster. Controls acceleration boost and recovery of extra headroom.

After resolving the common or gap-specific response, Eco caps it at 2 and Safe at 3. Normal and High retain the selected value; lower choices and 0 are never raised, and stored values are unchanged.

Additional headroom at levels 0–4 has a distance-limited hold. Reference D is speed × base TF + configured stopping distance, excluding extra headroom.

- Up to 1.2D: existing hold/recovery conditions apply.
- From 1.2D to 1.5D: the retained envelope and replenishment rate decrease while low-speed recovery restrictions ease.
- At or above 1.5D: recover at the selected level’s rate even for a pulling-away or stopped lead.

This does not erase the allowance instantly or directly add acceleration. Level 5 bypasses this opening-gap allowance. Separately, every level can retain a bounded braking-onset distance while both vehicles brake and close, then reduce it gradually as speed falls. Track replacement, invalid input or disengagement clears that memory.

With ample measured and predicted reserve, the comfort TF reference can temporarily decrease by up to 0.4 seconds with a 0.7-second reference floor. This automatic adjustment leaves saved settings and physical-obstacle constraints unchanged; it is not a brake cap or guaranteed safe headway. Actual vehicle clearance and comfort remain unvalidated.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Every response level uses TF with speed and driving-mode adjustments. The former levels 4–5 TF bypass is removed. Required braking and existing acceleration limits remain active.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponse -->

<!-- CARROT:SETTING:END LeadAccelResponse -->
