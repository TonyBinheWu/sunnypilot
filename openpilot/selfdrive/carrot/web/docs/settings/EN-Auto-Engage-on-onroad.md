<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_START" param="AutoEngage" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Auto Engage on onroad

**Menu:** Driving \> Start & Auto \> Engage

---

<!-- CARROT:SETTING:BEGIN AutoEngage -->
<a id="AutoEngage"></a>

## Auto Engage on onroad

`AutoEngage`

1: Steering Only, 2: Steering ON + Cruise Standby

<!-- CARROT:AUTO:BEGIN AutoEngage -->
<!-- CARROT:AUTO:SOURCE facts="c26423c838844400959dc0b36f4341e20b568e603699154464a6e38facc73671" semantic="5d795f951b628b849d1157749c4b492dddea109419cdb315856d2246614b812e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Segmented choice
- **Default:** `0`
- **Range:** `0` ~ `2`
- **Step:** `1`
- **Menu:** Driving \> Start & Auto \> Engage
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoEngage -->

<!-- CARROT:MANUAL:BEGIN AutoEngage -->
<!-- CARROT:REVIEW reviewed-for="5d795f951b628b849d1157749c4b492dddea109419cdb315856d2246614b812e" reviewed-at="2026-08-23T10:46:56+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

This setting selects the initial lateral-control and cruise-ready states at drive start. It does not immediately start steering, acceleration, or braking by itself.

- `0` — Does not automatically enable lateral control or cruise standby.
- `1` — Enables lateral control only.
- `2` — Enables lateral control and, on supported vehicles, cruise standby.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Change this while safely parked and verify the result on the next drive.

| Desired behavior | Settings to use together |
|---|---|
| Steering from drive start, manual cruise only | `AutoEngage=1`, `AlwaysLateral=1`, `AutoCruiseControl=0` |
| Steering from drive start, automatic cruise when conditions allow | `AutoEngage=2`, `AlwaysLateral=1`, `AutoCruiseControl=1` |
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> With `AlwaysLateral=0`, selecting `1` or `2` still does not provide actual steering while cruise is inactive. Use `AlwaysLateral=1` when steering must remain available independently of cruise.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoEngage -->

<!-- CARROT:SETTING:END AutoEngage -->
