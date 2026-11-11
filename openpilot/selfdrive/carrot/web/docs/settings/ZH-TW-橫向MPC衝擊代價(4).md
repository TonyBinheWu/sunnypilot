<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="LatMpcJerkCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 橫向MPC衝擊代價(4)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN LatMpcJerkCost -->
<a id="LatMpcJerkCost"></a>

## 橫向MPC衝擊代價(4)

`LatMpcJerkCost`

(車道模式) 值越低允許越快的轉向 — 會降低平滑度

<!-- CARROT:AUTO:BEGIN LatMpcJerkCost -->
<!-- CARROT:AUTO:SOURCE facts="3c80e88886cbc07f98c2c1d49ff803e90478493fce9dc79a43e86738e038ba1c" semantic="b03aeed762639a7ad9e574bc0a93999bce2ccf72dd07f737014001472e26b1fb" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `1`
- **範圍:** `0` ~ `200`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcJerkCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcJerkCost -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（LaneMode）調低可讓轉向更快，但平順性會降低。

- **調高：** 增加此項目的 MPC 代價與抑制權重。
- **調低：** 更容易允許該項動作。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

在相同車道及彎道重複測試，每次調整一項，同時比較路徑追蹤、轉向反應及平順度。
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 補充說明

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 不適當的數值可能降低轉向或縱向控制的穩定性與舒適度。每次只小幅調整一項，行為異常時恢復預設值。
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END LatMpcJerkCost -->

<!-- CARROT:SETTING:END LatMpcJerkCost -->
