<!-- CARROT:GENERATED schema="1" locale="en" group="BASIC_START" param="AlwaysLateral" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Always Lateral

**Menu:** Driving \> Start & Auto \> Engage

---

<!-- CARROT:SETTING:BEGIN AlwaysLateral -->
<a id="AlwaysLateral"></a>

## Always Lateral

`AlwaysLateral`

Allow lateral control even when cruise is not active. Steering waits for initial input readiness after system startup. Once passed, this check does not block again; existing runtime safety handling remains unchanged. Tesla can steer at true standstill; minimum steering-speed limits still apply while moving. On Tesla with the vehicle CAN extension, each distinct three-finger screen contact toggles this setting live, not Experimental Mode. OFF does not disengage steering under active cruise. Confirmed persistent CAN-controller errors or recurring Casper front-safety-system faults trigger an alert and disable always-on steering too; re-engagement is blocked until the fault clears. 0: OFF, 1: ON Hyundai/Kia CAN-FD loads a separate Panda Always Lateral authorization at startup. If it was OFF at startup, reboot while parked after turning it ON. Turning it OFF still stops host always-on steering immediately. Outside active cruise, Panda also requires wheel/driver-torque RX data no older than 100 ms. Tesla live toggling is unchanged.

<!-- CARROT:AUTO:BEGIN AlwaysLateral -->
<!-- CARROT:AUTO:SOURCE facts="25148a3b6feeac977d9e6de7c5576b25e8912191caecdbebd287713030ed4ce3" semantic="0dd1642d4ae06bd0308b3ae7e3b892138a13022b1d17d05aff0df4a2a40d5c08" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Start & Auto \> Engage
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AlwaysLateral -->

<!-- CARROT:MANUAL:BEGIN AlwaysLateral -->
<!-- CARROT:REVIEW reviewed-for="0dd1642d4ae06bd0308b3ae7e3b892138a13022b1d17d05aff0df4a2a40d5c08" reviewed-at="2026-11-17T15:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

- **On:** When lateral control is enabled in a forward-driving gear, steering can continue while cruise is off or after braking disengages cruise while driving.
- **Off:** Steering is available only while driving control is active.

This setting separates the steering and cruise activation states; it does not affect acceleration or braking.
On supported Tesla vehicles, steering can remain available at true standstill in a forward-driving gear when lateral control is already enabled. Minimum steering-speed limits still apply while moving; steering faults and a disabled lateral state still prevent steering.

After system startup, steering waits for the first confirmation of valid model, vehicle-parameter, pose, and other required inputs. Once passed, this startup check ends; later input interruptions or disengagement/reengagement do not rearm it. Existing runtime safety handling remains unchanged. Expiry of the startup waiting period alone does not pass this check.
Confirmed persistent CAN-controller errors or recurring Casper front-safety-system faults trigger an alert and disable always-on steering too; re-engagement is blocked until the fault clears.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

To start with steering available while keeping cruise manual, use `AutoEngage=1`, `AlwaysLateral=1`, and `AutoCruiseControl=0`. On the next drive, check steering once with cruise off and once while pressing the brake during motion.
Tesla with the vehicle CAN extension can toggle this setting live with each distinct three-finger infotainment contact. Release before repeating; held or duplicate presses do not repeat. Experimental/Chill mode and its confirmation are not changed or required. Existing saved values are preserved during upgrade. This is not an emergency disengagement gesture.
Hyundai/Kia CAN-FD loads a separate Panda Always Lateral authorization at startup. If it was OFF at startup, reboot while parked after turning it ON. Turning it OFF still stops host always-on steering immediately. Outside active cruise, Panda also requires wheel/driver-torque RX data no older than 100 ms. Tesla live toggling is unchanged.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> This setting does not turn lateral control on by itself. Lateral control must first be enabled by `AutoEngage` or the applicable vehicle button.
<!-- CARROT:NOTICE:END -->

Steering can stop below the vehicle-specific minimum steering speed even before the vehicle fully stops. It also remains off during steering faults, in a non-driving gear, or after a vehicle-button or cancel-button setting turns lateral control off.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AlwaysLateral -->

<!-- CARROT:SETTING:END AlwaysLateral -->
