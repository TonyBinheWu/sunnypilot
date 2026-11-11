<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="LatMpcPathCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 橫向MPC路徑代價(200)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN LatMpcPathCost -->
<a id="LatMpcPathCost"></a>

## 橫向MPC路徑代價(200)

`LatMpcPathCost`

(車道模式) 路徑跟隨權重 — 值越高越優先考慮路徑

<!-- CARROT:AUTO:BEGIN LatMpcPathCost -->
<!-- CARROT:AUTO:SOURCE facts="2981bec4c4b04898a58f988ff29d5b6f30103fb8b06b5820f81d7dc60d063804" semantic="b83cc299182908b4d8c01ed9a897df4983bc1c8e59c535005d5f9ddde372c233" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `200`
- **範圍:** `0` ~ `500`
- **步長:** `10`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcPathCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcPathCost -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（LaneMode）路徑追蹤權重：調高會更優先遵循路徑。

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
<!-- CARROT:MANUAL:END LatMpcPathCost -->

<!-- CARROT:SETTING:END LatMpcPathCost -->
