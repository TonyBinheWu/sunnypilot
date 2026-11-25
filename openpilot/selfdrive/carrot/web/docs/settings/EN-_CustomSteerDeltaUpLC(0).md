<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_LIMIT" param="CustomSteerDeltaUpLC" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# \_CustomSteerDeltaUpLC(0)

**Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits

---

<!-- CARROT:SETTING:BEGIN CustomSteerDeltaUpLC -->
<a id="CustomSteerDeltaUpLC"></a>

## \_CustomSteerDeltaUpLC(0)

`CustomSteerDeltaUpLC`

Torque Vehicle — Temporarily applies SteerDeltaUp during lane changes EV6 HDA2 torque steering on the ADAS ECU allows up to 2 units per 10 ms and honors a lower positive setting.

<!-- CARROT:AUTO:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:AUTO:SOURCE facts="4b4e8b881094920ead4d9e7f2efb360aa9b57f41e79bb2c5bc6b8ef23cc7e555" semantic="a269ff8291eb110176550d7c9962c300e661cb8701b0d25780bbf6bd978c1ba5" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `0`
- **Range:** `0` ~ `50`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Steering Limits
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CustomSteerDeltaUpLC -->

<!-- CARROT:MANUAL:BEGIN CustomSteerDeltaUpLC -->
<!-- CARROT:REVIEW reviewed-for="4c4f646026bac5f61b4baffbdf4b28f1bd790783dd022d744209c74a30c33e3e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Torque Vehicle — Temporarily applies SteerDeltaUp during lane changes.

- **Higher:** Increases the applicable steering-torque limit or rate.
- **Lower:** Reduces the limit or rate.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

On supported torque-control vehicles, adjust one item at a time and verify steering ramp-up and ramp-down in normal driving and lane changes.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> Incorrect values can reduce steering or longitudinal stability and comfort. Change one item in small steps and restore the default if behavior becomes abnormal.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CustomSteerDeltaUpLC -->

<!-- CARROT:SETTING:END CustomSteerDeltaUpLC -->
