<!-- CARROT:GENERATED schema="1" locale="en" group="CRUISE_GAP" param="SpeedTFFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Speed TF multiplier

**Menu:** Driving \> Cruise & Gap \> Follow Gap

---

<!-- CARROT:SETTING:BEGIN SpeedTFFactor -->
<a id="SpeedTFFactor"></a>

## Speed TF multiplier

`SpeedTFFactor`

TF multiplier at 100 km/h: 10=1.0x (unchanged), 20=2.0x. Starts at 1.0x when stopped and increases linearly with speed. Does not change following responsiveness.

<!-- CARROT:AUTO:BEGIN SpeedTFFactor -->
<!-- CARROT:AUTO:SOURCE facts="dad57d2b99e48665eb97b442e5dbce57626eaaa005cd44e69bc0939da42e4cd4" semantic="5a06220209167170871cd56a8bbad19e3a0ee27e7de4e1e4e83b573a1dc6126a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** 1.0× (`10`)
- **Range:** 1.0× (`10`) ~ 3.0× (`30`)
- **Step:** `1`
- **Options:** `10` 1.0×, `11` 1.1×, `12` 1.2×, `13` 1.3×, `14` 1.4×, `15` 1.5×, `16` 1.6×, `17` 1.7×, `18` 1.8×, `19` 1.9×, `20` 2.0×, `21` 2.1×, `22` 2.2×, `23` 2.3×, `24` 2.4×, `25` 2.5×, `26` 2.6×, `27` 2.7×, `28` 2.8×, `29` 2.9×, `30` 3.0×
- **Menu:** Driving \> Cruise & Gap \> Follow Gap
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedTFFactor -->

<!-- CARROT:MANUAL:BEGIN SpeedTFFactor -->
<!-- CARROT:REVIEW reviewed-for="84e34b1b5a1f71494a36b091cec0a6993009fc835fe70f30e264bd5cbe6db98b" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Higher values increase the selected base TF more at the same speed. The stopped value stays at base TF; the same linear slope continues above 100 km/h. Lead response level is unchanged.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

Setting 20 with base TF 0.50 s gives 0.50/0.75/1.00 s at 0/50/100 km/h, before driving-mode and deceleration adjustments. The old EnableSpeedTF value is not converted.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END SpeedTFFactor -->

<!-- CARROT:SETTING:END SpeedTFFactor -->
