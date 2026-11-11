<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="VEH_DEVICE" param="HardwareC3xLite" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# C3X Lite 硬體

**選單:** 車輛與硬體 \> 裝置硬體

---

<!-- CARROT:SETTING:BEGIN HardwareC3xLite -->
<a id="HardwareC3xLite"></a>

## C3X Lite 硬體

`HardwareC3xLite`

僅在 C3X Lite 上啟用。使用 GPIO 蜂鳴器代替揚聲器/功放，並停用音訊和記錄記錄程序。更改後請重新啟動裝置。

<!-- CARROT:AUTO:BEGIN HardwareC3xLite -->
<!-- CARROT:AUTO:SOURCE facts="6b4b26c75b186ba1c903ade1b8ed207a47b47783f143de4cd515bc38fa623b5a" semantic="1d1f4a2f5d6f90a2445f2e04e4f643f09e565be8708d71ac3d2190980ba0455c" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 車輛與硬體 \> 裝置硬體
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HardwareC3xLite -->

<!-- CARROT:MANUAL:BEGIN HardwareC3xLite -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 僅限 C3X Lite 使用。以 GPIO 蜂鳴器取代喇叭／擴大機，並停用音訊與記錄程序。變更後須重新啟動裝置。
- **關閉：** 不套用此功能，維持既有行為。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

僅在裝置硬體完全符合時變更，接著重新啟動並確認音效、記錄及程序狀態。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 在標準裝置上啟用此設定，可能停用音訊與記錄程序。變更後須重新啟動裝置。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HardwareC3xLite -->

<!-- CARROT:SETTING:END HardwareC3xLite -->
