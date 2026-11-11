<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="SYS_NET" param="HotspotOnBoot" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 開啟熱點 (0)

**選單:** 系統 \> 網路與地圖

---

<!-- CARROT:SETTING:BEGIN HotspotOnBoot -->
<a id="HotspotOnBoot"></a>

## 開啟熱點 (0)

`HotspotOnBoot`

在 COMMA 中插入 USIM 卡時自動開啟熱點的功能

<!-- CARROT:AUTO:BEGIN HotspotOnBoot -->
<!-- CARROT:AUTO:SOURCE facts="4b081fdc1bed47bc10f2f78648c7e3b6f0f3574f7efa39a22858c394d99790d5" semantic="f60b11ad1a9e01c9a2140827ce36a15ff5fc686b902d45a7c578afb846582f96" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 系統 \> 網路與地圖
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HotspotOnBoot -->

<!-- CARROT:MANUAL:BEGIN HotspotOnBoot -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 有可用行動網路連線時，請求在開機後自動啟動熱點。
- **關閉：** 開機時不自動啟用熱點。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

有網路連線時變更，並於下次連線或開啟地圖時確認。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 自動啟動熱點需要裝置具備可用的 USIM 與行動網路。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HotspotOnBoot -->

<!-- CARROT:SETTING:END HotspotOnBoot -->
