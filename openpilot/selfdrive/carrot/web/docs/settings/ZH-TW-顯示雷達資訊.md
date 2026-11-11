<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_SCREEN" param="ShowRadarInfo" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示雷達資訊

**選單:** 顯示 \> 資訊顯示

---

<!-- CARROT:SETTING:BEGIN ShowRadarInfo -->
<a id="ShowRadarInfo"></a>

## 顯示雷達資訊

`ShowRadarInfo`

0: 無, 1: 顯示, 2: + 相對位置, 3: 停止的障礙物

<!-- CARROT:AUTO:BEGIN ShowRadarInfo -->
<!-- CARROT:AUTO:SOURCE facts="eb56aa9ba80db2fb38300315655eff48b15e4d0845461fbe55ab91e4a94dd7e4" semantic="fb6304349c3a0b1cfa84b4b40b7437938cd0f850a9949f10e2c90253a72c5c3d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `0`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 顯示 \> 資訊顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowRadarInfo -->

<!-- CARROT:MANUAL:BEGIN ShowRadarInfo -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 無
- `1` — 顯示
- `2` — 加上相對位置
- `3` — 靜止障礙物

在使用 ARS 顯示串流的 RAV4 2022 標準裝置行車畫面中，`3` 也會將相鄰車道物體與控制用前車分開顯示。移動物體顯示速度，慢速或靜止物體顯示星號；看得見的物體不一定是煞車目標。

仍保留 CRC、物體資料時效、速度有效性及距離條件。過期、無效或空白輸入會清除顯示。模式 `1`、`2`、其他接收端及網頁／mici 畫面沿用既有流程。此功能不會新增 Toyota 側角雷達支援。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

檢查行車畫面的配置及可讀性，只啟用需要的資訊。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowRadarInfo -->

<!-- CARROT:SETTING:END ShowRadarInfo -->
