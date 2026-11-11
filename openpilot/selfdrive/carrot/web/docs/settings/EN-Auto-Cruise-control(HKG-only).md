<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_AUTOCRUISE" param="AutoCruiseControl" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Auto Cruise control(HKG only)

**Menu:** Driving \> Start & Auto \> Auto Cruise

---

<!-- CARROT:SETTING:BEGIN AutoCruiseControl -->
<a id="AutoCruiseControl"></a>

## Auto Cruise control(HKG only)

`AutoCruiseControl`

1:Softhold + Auto Cruise, 2:if softhold error

<!-- CARROT:AUTO:BEGIN AutoCruiseControl -->
<!-- CARROT:AUTO:SOURCE facts="c0213b38a929b3d92d65a07d9ea812e849bf90bdf17dff447106eeef92a0ef82" semantic="686814b2afc5769591dcd6e77c8b4ea3b65cc4c23c4b4437b0e289a38f9273d5" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Driving \> Start & Auto \> Auto Cruise
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoCruiseControl -->

<!-- CARROT:MANUAL:BEGIN AutoCruiseControl -->
<!-- CARROT:REVIEW reviewed-for="686814b2afc5769591dcd6e77c8b4ea3b65cc4c23c4b4437b0e289a38f9273d5" reviewed-at="2026-08-23T10:46:56+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

This setting automatically activates cruise acceleration and braking when its conditions are met. It does not directly enable lateral control or limit steering torque.

- `0` — Disables automatic cruise and soft hold. Manual cruise and Always Lateral remain available.
- `1` — Enables automatic cruise with the standard soft-hold behavior.
- `2` — Enables automatic cruise with the soft-hold behavior intended for vehicles that report an error with the standard mode.
- `3` — The current control path uses the same automatic-cruise and soft-hold behavior as `2`.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use `0` when automatic cruise is not wanted and `1` for normal automatic-cruise operation. Use `2` only when the vehicle reports a soft-hold error with `1`, then compare the activation point under the same start, accelerator, and lead-vehicle conditions.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> With `AlwaysLateral=1`, steering continues while lateral control is enabled even when automatic cruise is off. With `AlwaysLateral=0`, steering uses the same active driving state as cruise, so steering can appear to switch with automatic cruise.
<!-- CARROT:NOTICE:END -->

This setting is for Hyundai and Kia vehicles; actual availability depends on the vehicle's longitudinal-control configuration.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoCruiseControl -->

<!-- CARROT:SETTING:END AutoCruiseControl -->
