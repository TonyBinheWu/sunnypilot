<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="HUD_RADAR" param="ClusterHudRadarInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 外部 HUD 雷達資訊(4)

**選單:** 顯示 \> 外部HUD \> 雷達顯示

---

<!-- CARROT:SETTING:BEGIN ClusterHudRadarInfo -->
<a id="ClusterHudRadarInfo"></a>

## 外部 HUD 雷達資訊(4)

`ClusterHudRadarInfo`

0: 關閉 1: 速度(僅車輛) 2: 速度,距離(僅車輛) 3: 速度(全部) 4: 速度,距離(全部)

<!-- CARROT:AUTO:BEGIN ClusterHudRadarInfo -->
<!-- CARROT:AUTO:SOURCE facts="fa33367c01d6ce31b15f0066b10d9d46af59598b3c463ac851ad85360791d3aa" semantic="05cc3268420daab3de56e5bbd791d233fe6c5cccda542fd4688e6a5bd63dfa2a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 選擇
- **預設值:** `4`
- **範圍:** `0` ~ `4`
- **步長:** `1`
- **選單:** 顯示 \> 外部HUD \> 雷達顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudRadarInfo -->

<!-- CARROT:MANUAL:BEGIN ClusterHudRadarInfo -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 關閉
- `1` — 速度（僅車輛）
- `2` — 速度、距離（僅車輛）
- `3` — 速度（全部）
- `4` — 速度、距離（全部）
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在外接 HUD 觀察相同前車及周圍物體，確認顯示目標、距離及來源區分。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudRadarInfo -->

<!-- CARROT:SETTING:END ClusterHudRadarInfo -->
