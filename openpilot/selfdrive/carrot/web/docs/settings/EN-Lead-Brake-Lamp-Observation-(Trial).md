<!-- CARROT:GENERATED schema="1" locale="en" group="SPEED_TRAFFIC" param="LeadBrakeLights" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Lead Brake Lamp Observation (Trial)

**Menu:** Driving \> Speed & Decel \> Traffic Light

---

<!-- CARROT:SETTING:BEGIN LeadBrakeLights -->
<a id="LeadBrakeLights"></a>

## Lead Brake Lamp Observation (Trial)

`LeadBrakeLights`

0: Off (default). 1: Display/log a central brake-lamp candidate on the immediate radar/vision-matched lead in signal modes 1/2. BRAKE? is a candidate, not verified braking; missing evidence is unknown, not off. No braking or departure control. Skips busy signal iterations, turns and uncertain lead association. Signal mode 0 disables all auxiliary work.

<!-- CARROT:AUTO:BEGIN LeadBrakeLights -->
<!-- CARROT:AUTO:SOURCE facts="0fa2b265e92306b1fcbe6ef73a06058cd27e6207f22f8e64005b4fb111198e6d" semantic="1c52b548b46d979bac0118c3daafe7304a87141b48ac8f9662b240448cd8289a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `0`
- **Range:** `0` ~ `1`
- **Menu:** Driving \> Speed & Decel \> Traffic Light
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadBrakeLights -->

<!-- CARROT:MANUAL:BEGIN LeadBrakeLights -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END LeadBrakeLights -->

<!-- CARROT:SETTING:END LeadBrakeLights -->
