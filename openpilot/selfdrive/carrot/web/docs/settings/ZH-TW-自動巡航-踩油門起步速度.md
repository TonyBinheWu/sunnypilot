<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="BASIC_AUTOCRUISE" param="AutoGasTokSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自動巡航: 踩油門起步速度

**選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航

---

<!-- CARROT:SETTING:BEGIN AutoGasTokSpeed -->
<a id="AutoGasTokSpeed"></a>

## 自動巡航: 踩油門起步速度

`AutoGasTokSpeed`

僅在設定速度以上執行 — GasTab: 踩油門 0.6 秒

<!-- CARROT:AUTO:BEGIN AutoGasTokSpeed -->
<!-- CARROT:AUTO:SOURCE facts="ecb8dc25f507769691acbf94124981e9481a26af73d0d1a7c45c26b8ed78652f" semantic="566c9988c19eba63fd6ef647f6a0e4a6d6ba01d071de04c633eb540cc2cf4441" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `0km/h`
- **範圍:** `0km/h` ~ `200km/h`
- **步長:** `5`
- **顯示單位:** `km/h`
- **選單:** 駕駛控制 \> 啟動·自動 \> 自動巡航
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasTokSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasTokSpeed -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

僅在高於設定速度時運作；GasTab：輕踩油門踏板 0.6 秒。

- **調高：** 提高適用的速度或速度門檻。
- **調低：** 降低速度或門檻。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同起步、油門及前車條件下，每次調整一項，比較巡航啟用時機及設定速度。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasTokSpeed -->

<!-- CARROT:SETTING:END AutoGasTokSpeed -->
