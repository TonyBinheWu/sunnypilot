<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_PATH" param="ShowPathColorCruiseOff" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Path Color:CruiseOFF(1)

**Menu:** Display \> Path Display

---

<!-- CARROT:SETTING:BEGIN ShowPathColorCruiseOff -->
<a id="ShowPathColorCruiseOff"></a>

## Show Path Color:CruiseOFF(1)

`ShowPathColorCruiseOff`

(+10:stroke)0(R),1(O),2(Y),3(B),5(N),6(V),7(K),8(W),9(B)

<!-- CARROT:AUTO:BEGIN ShowPathColorCruiseOff -->
<!-- CARROT:AUTO:SOURCE facts="6bacec663b4912db51bcfa66a964437cf54e9c6a1536924e8f51ed5a0ab3f9f4" semantic="a49ee2ac59951411b6a5ff92f21e37706f20d0ab78df06c01f21fdaff8b23119" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `1`
- **Range:** `0` ~ `19`
- **Step:** `1`
- **Menu:** Display \> Path Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColorCruiseOff -->

<!-- CARROT:MANUAL:BEGIN ShowPathColorCruiseOff -->
<!-- CARROT:REVIEW reviewed-for="a49ee2ac59951411b6a5ff92f21e37706f20d0ab78df06c01f21fdaff8b23119" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

`0`–`9` select red, orange, yellow, green, blue, navy, violet, brown, white, and black for the cruise-off path. `10`–`19` add an emphasis outline to the matching color.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Switch cruise and lane-mode states on the driving display and verify that path shape and color change as intended.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColorCruiseOff -->

<!-- CARROT:SETTING:END ShowPathColorCruiseOff -->
