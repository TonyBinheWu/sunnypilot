<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_CANFD" param="CanfdBlinkerTest" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Parked SPAS indicator test

**選單:** 車輛與硬體 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdBlinkerTest -->
<a id="CanfdBlinkerTest"></a>

## Parked SPAS indicator test

`CanfdBlinkerTest`

With SPAS enabled after reboot: 1/2 acknowledged continuous left/right, 3/4 acknowledged short-plus-hold. Parked coexistence comparisons on Ioniq5PE only: 5/6 continuous, 7/8 0.2-second pulse plus existing hold, 9/10 pulse only. 11/12 one packet per new stock receipt, ending 0.1s after lamp confirmation and at most 0.5s, then existing confirmed hold for a 10-second total. 13/14 repeat only SPAS after fresh stock reception for up to 10 seconds, without the existing hold. Coexistence tests send no ECU diagnostics. P, zero speed and inactive controls required throughout; 7/8/11/12/13/14 last 10 seconds total, others at most 3 seconds; coexistence cooldown is 30 seconds from start. Select 0 to cancel or before repeating. Resets at startup. 15/16: supplied-patch left/right parked comparison: APRK 1003, then 288301 after five controller frames, SPAS on even frames without waiting for replies. Uses actual controller frame/native packer, at most 10 seconds, 1001 restore on end or CAN/vehicle guard failure. 17/18: parked left/right 0x3C1 lever replay at 20Hz, max 10s; no APRK/SPAS, cancel on driver/input/CAN change.

<!-- CARROT:AUTO:BEGIN CanfdBlinkerTest -->
<!-- CARROT:AUTO:SOURCE facts="e422dc3a942c006955913f0bcbe0b4ce0277024455e1582b4f7ab6d47debd6b7" semantic="fb7269f5f606690f79807f0151cfbd3c0ce1118aee4eacbe624733fae2caa93e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0`
- **範圍:** `0` ~ `18`
- **步長:** `1`
- **選單:** 車輛與硬體 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdBlinkerTest -->

<!-- CARROT:MANUAL:BEGIN CanfdBlinkerTest -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CanfdBlinkerTest -->

<!-- CARROT:SETTING:END CanfdBlinkerTest -->
