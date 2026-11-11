<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_RADAR" param="ClusterHudRadarDisplay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 雷達顯示選項(0)

**選單:** 顯示 \> 外部HUD \> 雷達顯示

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarDisplay -->
<a id="ClusterHudRadarDisplay"></a>

## 外部 HUD 雷達顯示選項(0)

`ClusterHudRadarDisplay`

0: 預設(合併相近雷達點) 1: 詳細(不合並雷達點)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarDisplay -->
<!-- CARROT:AUTO:SOURCE facts="e90f46640f4c71d5277e62c3d13d55798f0121808fe925de130cfb4ff7fed233" semantic="c0542f70ce7ff639693facf6fed2c23f3d14b8dd10885a9e546818549e5afdce" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 顯示 \> 外部HUD \> 雷達顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarDisplay -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarDisplay -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 預設（合併鄰近雷達點）
- `1` — 詳細（原始雷達點）
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在外接 HUD 觀察相同前車及周圍物體，確認顯示目標、距離及來源區分。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarDisplay -->

<!-- CARROT:SETTING:END ClusterHudRadarDisplay -->
