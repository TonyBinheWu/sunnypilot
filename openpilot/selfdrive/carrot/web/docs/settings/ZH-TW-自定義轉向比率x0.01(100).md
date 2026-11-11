<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="SteerRatioRate" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 自定義轉向比率x0.01(100)

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN SteerRatioRate -->
<a id="SteerRatioRate"></a>

## 自定義轉向比率x0.01(100)

`SteerRatioRate`

實時轉向比應用比例 (需要 CustomSR 設定為 0)

<!-- CARROT:AUTO:BEGIN SteerRatioRate -->
<!-- CARROT:AUTO:SOURCE facts="ca1ee37a0221d87cfd685d7867e9237a03698a6d2aae4411ee3e7855287c0366" semantic="3dcdc5b26050ba384382fe8733f365d2de9ff1bc73e56b23703f73b6dce4381b" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100%`
- **範圍:** `30%` ~ `200%`
- **步長:** `1`
- **顯示單位:** `%`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SteerRatioRate -->

<!-- CARROT:MANUAL:BEGIN SteerRatioRate -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

LiveSteerRatio 套用比例（CustomSR 須設為 0）。

- **調高：** 增加套用至學習所得轉向比的倍率。
- **調低：** 降低該倍率。

此設定也適用於 VW MEB（含 ID.4）；選定有效的手動轉向比會略過此倍率。儲存倍率超出允許範圍時，回復使用未縮放的學習轉向比。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同直路及平緩彎道，每次小幅調整一項，檢查延遲、振盪及駕駛介入後的恢復。

先前被忽略的 ID.4 設定值會在更新後生效。使用 `CustomSR=0` 及 `SteerRatioRate=100%` 可保留原本學習所得的轉向比。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 只有 `CustomSR` 為 `0` 時，此倍率才會套用至學習所得的轉向比。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SteerRatioRate -->

<!-- CARROT:SETTING:END SteerRatioRate -->
