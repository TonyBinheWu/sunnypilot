<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_AUTOCRUISE" param="AutoGasSyncSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動更新巡航速度

**選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航

---

<!-- CARROT:SETTING:BEGIN AutoGasSyncSpeed -->
<a id="AutoGasSyncSpeed"></a>

## 自動更新巡航速度

`AutoGasSyncSpeed`

如果踩下油門且速度超過設定速度，則更新設定速度

<!-- CARROT:AUTO:BEGIN AutoGasSyncSpeed -->
<!-- CARROT:AUTO:SOURCE facts="90f971c107364d490d3e2baecbb7237ac6979f26fbe0b39ea65ef14b73c4f7da" semantic="b7d50e021ae02dfaf5a91c4919bed99b902eecbb6a56c177e5cbdc093c729db0" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 開關
- **預設值:** `0`
- **範圍:** `0` ~ `1`
- **選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasSyncSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasSyncSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- **開啟：** 操作油門使車速高於巡航設定速度後，將設定速度提高至目前車速。
- **關閉：** 操作油門後仍保留既有巡航設定速度。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同起步、油門及前車條件下，每次調整一項，比較巡航啟用時機及設定速度。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasSyncSpeed -->

<!-- CARROT:SETTING:END AutoGasSyncSpeed -->
