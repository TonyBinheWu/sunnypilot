<!-- CARROT:GENERATED schema="1" locale="en" group="VEH_DEVICE" param="CommaPedalEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Comma Pedal longitudinal control

**Menu:** Vehicle & Hardware \> Device Hardware

---

<!-- CARROT:SETTING:BEGIN CommaPedalEnabled -->
<a id="CommaPedalEnabled"></a>

## Comma Pedal longitudinal control

`CommaPedalEnabled`

Allows longitudinal control through a Comma Pedal device in vehicles without ACC. Requires CC\_ONLY\_CAR and the vehicle's Cruise ready state to be off. When Cruise ready is on, OEM cruise control takes priority and Comma Pedal control is unavailable.

<!-- CARROT:AUTO:BEGIN CommaPedalEnabled -->
<!-- CARROT:AUTO:SOURCE facts="f63c5b14b9d98e7bfdb1bf35e44c6e7b88ae795752eb99b3502f55f03b56e822" semantic="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Vehicle & Hardware \> Device Hardware
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CommaPedalEnabled -->

<!-- CARROT:MANUAL:BEGIN CommaPedalEnabled -->
<!-- CARROT:REVIEW reviewed-for="5cbde9f56254e3cc6a7304e4b3cf2da6b07f9ec7b1a494bfc3889cd0e17da671" reviewed-at="2026-11-03T12:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Allows pedal control on CC_ONLY_CAR vehicles with an explicit profile, detected device and satisfied safety conditions. The current profile is for Kia Ray EV. OEM Cruise ready or engagement, invalid inputs, braking or driver accelerator input blocks pedal output.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Find the setting under Vehicle and hardware → Device hardware. Confirm the vehicle and pedal profile, then restart after changing the setting to apply vehicle parameters and the Panda firmware update.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

CarrotPilot vehicle operation, braking and standstill holding require separate validation. The contributor’s reported limited acceleration remains unresolved.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CommaPedalEnabled -->

<!-- CARROT:SETTING:END CommaPedalEnabled -->
