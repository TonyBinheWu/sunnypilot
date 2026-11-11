<!-- CARROT:GENERATED schema="1" locale="en" group="SYS_CAMERA" param="UseWideCamera" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Use Wide Road Camera

**Menu:** System \> Camera

---

<!-- CARROT:SETTING:BEGIN UseWideCamera -->
<a id="UseWideCamera"></a>

## Use Wide Road Camera

`UseWideCamera`

Enabled by default. Turn this off only on a device with a failed wide road camera. When off, camerad excludes the wide camera from synchronization and modeld reuses the narrow road image for both model inputs. Camera coverage and model performance may change. Reboot the device after changing.

<!-- CARROT:AUTO:BEGIN UseWideCamera -->
<!-- CARROT:AUTO:SOURCE facts="90df3f1573d165b6970e3a78a959d6d6c94822f732a3e3aac992c6e5c4e5ab28" semantic="98f6143429525738b1a1748e10af5089802e78c1eeeb632ec050ee74ca08fd18" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **Type:** Toggle
- **Default:** `1`
- **Range:** `0` ~ `1`
- **Menu:** System \> Camera
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END UseWideCamera -->

<!-- CARROT:MANUAL:BEGIN UseWideCamera -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END UseWideCamera -->

<!-- CARROT:SETTING:END UseWideCamera -->
