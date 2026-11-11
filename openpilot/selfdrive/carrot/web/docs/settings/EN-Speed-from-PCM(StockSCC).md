<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_AUX" param="SpeedFromPCM" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Speed from PCM(StockSCC)

**Menu:** Vehicle & Hardware \> Vehicle Aux

---

<!-- CARROT:SETTING:BEGIN SpeedFromPCM -->
<a id="SpeedFromPCM"></a>

## Speed from PCM(StockSCC)

`SpeedFromPCM`

PCM vehicle speed control. 0: Curve/Camera Deceleration + Long, 1: Stock set speed without button spamming, 2: Curve/Camera Decel, 3: Honda/Toyota (Toyota/Lexus use stock set speed; does not switch longitudinal mode)

<!-- CARROT:AUTO:BEGIN SpeedFromPCM -->
<!-- CARROT:AUTO:SOURCE facts="5536472dcfb6e5b296339113ca1bb5b5fe2dc31dd50c48a23fde1a3e3b181c33" semantic="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `2`
- **Range:** `0` ~ `3`
- **Step:** `1`
- **Menu:** Vehicle & Hardware \> Vehicle Aux
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedFromPCM -->

<!-- CARROT:MANUAL:BEGIN SpeedFromPCM -->
<!-- CARROT:REVIEW reviewed-for="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

The selected value changes behavior as follows.

- `0` — Curve/Camera Deceleration + Long
- `1` — No Button Spamming (Stock SCC)
- `2` — Curve/Camera Decel
- `3` — Honda/Toyota
For Toyota/Lexus, `3` uses stock SET/RES speed as the base control target and stock cluster set speed for display. Mode `1` also uses stock set speed; `0` and `2` retain existing Carrot speed selection. Honda mode `3` is unchanged. This setting does not switch the longitudinal controller or radar availability.

Mode `0` has one exception: on `TOYOTA_RAV4_TSS2_2022` with PCM and openpilot direct longitudinal control, stock set-speed changes or disabled-to-enabled cruise transitions observed through valid CAN update the base target. An initially enabled sample only establishes a reference; local button or Bluetooth speed changes take priority in the same cycle, lower lead/curve/map targets remain effective, and no RES/SET CAN transmission is added.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change one item at a time only on supported vehicles, then verify steering or stock SCC behavior on the next drive.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> A value that does not match the vehicle control configuration can change steering or stock-SCC behavior.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SpeedFromPCM -->

<!-- CARROT:SETTING:END SpeedFromPCM -->
