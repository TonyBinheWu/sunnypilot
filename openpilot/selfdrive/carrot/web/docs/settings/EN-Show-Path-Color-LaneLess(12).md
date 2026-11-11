<!-- CARROT:GENERATED schema="1" locale="en" group="DISP_PATH" param="ShowPathColor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Show Path Color:LaneLess(12)

**Menu:** Display \> Path Display

---

<!-- CARROT:SETTING:BEGIN ShowPathColor -->
<a id="ShowPathColor"></a>

## Show Path Color:LaneLess(12)

`ShowPathColor`

(+10:stroke)0(R),1(O),2(Y),3(B),5(N),6(V),7(K),8(W),9(B),20:Auto

<!-- CARROT:AUTO:BEGIN ShowPathColor -->
<!-- CARROT:AUTO:SOURCE facts="966ab2f241aa80e630980fa2cca3a186b079c73db864948bb320fe414b3f0bbc" semantic="fb7730745b0900682cd27aff93d72dbb7d8d94329f9989bc2022c096a6e257db" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Select
- **Default:** `12`
- **Range:** `0` ~ `20`
- **Step:** `1`
- **Menu:** Display \> Path Display
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowPathColor -->

<!-- CARROT:MANUAL:BEGIN ShowPathColor -->
<!-- CARROT:REVIEW reviewed-for="fb7730745b0900682cd27aff93d72dbb7d8d94329f9989bc2022c096a6e257db" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

`0`–`9` select red, orange, yellow, green, blue, navy, violet, brown, white, and black. `10`–`19` add an emphasis outline to the matching color, and `20` selects color automatically from driving state.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Switch cruise and lane-mode states on the driving display and verify that path shape and color change as intended.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowPathColor -->

<!-- CARROT:SETTING:END ShowPathColor -->
