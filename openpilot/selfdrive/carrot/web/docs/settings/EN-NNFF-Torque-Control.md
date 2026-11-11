<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_TORQUE_COEFF" param="NNFF" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NNFF Torque Control

**Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients

---

<!-- CARROT:SETTING:BEGIN NNFF -->
<a id="NNFF"></a>

## NNFF Torque Control

`NNFF`

Neural-network feedforward for torque steering. Enabling selects torque-controller tuning on vehicles without angle control and uses NNFF when a matching model is available. Vehicles supported by comma's own NNFF retain that path's precedence. Disabling turns off this NNFF option without changing NNFFLite. Defaults to off and appears only in Carrot Web search. Changes apply at the next onroad start or after a device reboot. Does not apply to angle-control vehicles.

<!-- CARROT:AUTO:BEGIN NNFF -->
<!-- CARROT:AUTO:SOURCE facts="5d317497fa6933398a05feb2649f404ccc54f2e9823006487693daf11df44d09" semantic="bf1b67050f021288a3be062698bf0689878aedc8c326f0f30176feec716d40f2" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Steering \> Advanced Torque \> Torque Coefficients
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END NNFF -->

<!-- CARROT:MANUAL:BEGIN NNFF -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END NNFF -->

<!-- CARROT:SETTING:END NNFF -->
