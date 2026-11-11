<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="DISP_SCREEN" param="ShowTpms" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 顯示胎壓 (TPMS) 資訊

**選單:** 顯示 \> 資訊顯示

---

<!-- CARROT:SETTING:BEGIN ShowTpms -->
<a id="ShowTpms"></a>

## 顯示胎壓 (TPMS) 資訊

`ShowTpms`

0: 無, 1: 上方, 2: 下方, 3: 兩側 ※ 不適用於 C4 (MICI)

<!-- CARROT:AUTO:BEGIN ShowTpms -->
<!-- CARROT:AUTO:SOURCE facts="90f1f9f45d65806c04d3e2a4c9dd3d72842f2d3cccfdf908c65547ae95369aa4" semantic="fd79f1bf1968efdfc0592e51e5336d2ab76734d8ffd69c233cc4444a22b4c036" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 分段選擇
- **預設值:** `1`
- **範圍:** `0` ~ `3`
- **步長:** `1`
- **選單:** 顯示 \> 資訊顯示
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowTpms -->

<!-- CARROT:MANUAL:BEGIN ShowTpms -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

選定值會依下列方式改變行為。

- `0` — 無
- `1` — 上方
- `2` — 下方
- `3` — 兩者皆使用
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

檢查行車畫面的配置及可讀性，只啟用需要的資訊。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ShowTpms -->

<!-- CARROT:SETTING:END ShowTpms -->
