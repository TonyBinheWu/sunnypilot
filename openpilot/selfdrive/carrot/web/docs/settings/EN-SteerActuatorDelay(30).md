<!-- CARROT:GENERATED schema="1" locale="en" group="STEER_FEEL" param="SteerActuatorDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# SteerActuatorDelay(30)

**Menu:** Driving \> Steering \> Steering Feel

---

<!-- CARROT:SETTING:BEGIN SteerActuatorDelay -->
<a id="SteerActuatorDelay"></a>

## SteerActuatorDelay(30)

`SteerActuatorDelay`

Steering response delay compensation: 30=0.30s, 0=LiveDelay. Higher values compensate earlier. Center of gravity ratio also affects corner entry. Keep SAD and SR unchanged when comparing that ratio.

<!-- CARROT:AUTO:BEGIN SteerActuatorDelay -->
<!-- CARROT:AUTO:SOURCE facts="5d58aebdfa0af0b883a55a69d06cf4be959fce6f109fa676c7a9a0221ed2abe9" semantic="2d1e59de8edc91af92b92e8bcb989bbc50e68cca9731d896bd7f990032ce4097" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Number
- **Default:** `30`
- **Range:** `0` ~ `300`
- **Step:** `1`
- **Menu:** Driving \> Steering \> Steering Feel
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SteerActuatorDelay -->

<!-- CARROT:MANUAL:BEGIN SteerActuatorDelay -->
<!-- CARROT:REVIEW reviewed-for="d72d913592441b3ae02dcad9b3d9db17842df189841f5d0a1eabaeac094725c6" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### Behavior

Steering Delay Value — Higher values steer earlier. 0 means Live Delay.

- **Higher:** Assumes more steering delay and requests steering earlier.
- **Lower:** Reduces steering lead compensation.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### Usage

Use small, one-at-a-time changes on the same straight and gentle curve, checking delay, oscillation, and recovery after driver input.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### Reference

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0` uses the live estimated steering delay instead of a fixed value.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SteerActuatorDelay -->

<!-- CARROT:SETTING:END SteerActuatorDelay -->
