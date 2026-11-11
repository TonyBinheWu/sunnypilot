<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_AUTOCRUISE" param="CruiseOnDist" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 巡航開啟距離(0cm)

**選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航

---

<!-- CARROT:SETTING:BEGIN CruiseOnDist -->
<a id="CruiseOnDist"></a>

## 巡航開啟距離(0cm)

`CruiseOnDist`

鬆開油門且前車靠近時開啟巡航

<!-- CARROT:AUTO:BEGIN CruiseOnDist -->
<!-- CARROT:AUTO:SOURCE facts="a13d4bdb39729c6efd3c2620c870bb610c26628d1248db8bfcbf37d8da08dcd4" semantic="0c44a52dc53d02fb2b5c312b7ff88bdfab957c811fecd2c138ecd67868f032bb" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0cm`
- **範圍:** `0cm` ~ `2500cm`
- **步長:** `50`
- **顯示單位:** `cm`
- **選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseOnDist -->

<!-- CARROT:MANUAL:BEGIN CruiseOnDist -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

放開踏板且接近前車時啟用巡航。

- **調高：** 增加適用的距離或跟車間距。
- **調低：** 減少距離或跟車間距。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同起步、油門及前車條件下，每次調整一項，比較巡航啟用時機及設定速度。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END CruiseOnDist -->

<!-- CARROT:SETTING:END CruiseOnDist -->
