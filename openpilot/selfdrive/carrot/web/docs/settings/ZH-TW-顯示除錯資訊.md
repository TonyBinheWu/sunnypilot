<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_SCREEN" param="ShowDebugUI" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示除錯資訊

**選單:** 顯示 \> 資訊顯示

---

<!-- CARROT:SETTING:BEGIN ShowDebugUI -->
<a id="ShowDebugUI"></a>

## 顯示除錯資訊

`ShowDebugUI`

顯示除錯資訊

<!-- CARROT:AUTO:BEGIN ShowDebugUI -->
<!-- CARROT:AUTO:SOURCE facts="c099a4cc0723df19d8d0c484c7553ca54ee8929ebbbbb565e8caa9cdf6b9cca5" semantic="5427f7c6ad263c8644a81441bc61043f741eccdf5c7938a34fb92f7a0320090d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `1`
- **範圍:** `0` ~ `2`
- **步長:** `1`
- **選單:** 顯示 \> 資訊顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowDebugUI -->

<!-- CARROT:MANUAL:BEGIN ShowDebugUI -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

- `0` — 隱藏除錯資訊。
- `1`、`2` — 目前實作中，兩者都會在行車畫面顯示除錯資訊。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

檢查行車畫面的配置及可讀性，只啟用需要的資訊。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowDebugUI -->

<!-- CARROT:SETTING:END ShowDebugUI -->
