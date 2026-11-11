<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_FEEL" param="LatSmoothSec" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 轉向平滑時間(30)

**選單:** 駕駛控制 \> 轉向 \> 轉向手感

---

<!-- CARROT:SETTING:BEGIN LatSmoothSec -->
<a id="LatSmoothSec"></a>

## 轉向平滑時間(30)

`LatSmoothSec`

轉向平滑值 — 值越高越平滑

<!-- CARROT:AUTO:BEGIN LatSmoothSec -->
<!-- CARROT:AUTO:SOURCE facts="78392d0a974f1b59630fbc95f4eadaddc39e740b60786d920bbd139f958c867f" semantic="42a46c7c6b551635f61326eed6731f5eccaa1f0669f7bb23fa20a4f8626c95c2" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `13`
- **範圍:** `1` ~ `30`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 轉向手感
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatSmoothSec -->

<!-- CARROT:MANUAL:BEGIN LatSmoothSec -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

橫向平滑值：數值越高越平順。

- **調高：** 讓轉向變化更平順、較緩慢。
- **調低：** 回應更快，但平順性可能較差。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同直路及平緩彎道，每次小幅調整一項，檢查延遲、振盪及駕駛介入後的恢復。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatSmoothSec -->

<!-- CARROT:SETTING:END LatSmoothSec -->
