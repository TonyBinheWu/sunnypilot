<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="LatMpcMotionCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 橫向MPC運動代價(7)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN LatMpcMotionCost -->
<a id="LatMpcMotionCost"></a>

## 橫向MPC運動代價(7)

`LatMpcMotionCost`

(車道模式) 航向權重

<!-- CARROT:AUTO:BEGIN LatMpcMotionCost -->
<!-- CARROT:AUTO:SOURCE facts="e395ca54c07e88b4052db594d62fd8087fc7fb91499fc25876f627277d54e083" semantic="1bdf8d77309360a95334d5df9779a59844b5330500ee823a8f43986ad8d5667f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `7`
- **範圍:** `0` ~ `500`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcMotionCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcMotionCost -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（LaneMode）航向權重。

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
<!-- CARROT:MANUAL:END LatMpcMotionCost -->

<!-- CARROT:SETTING:END LatMpcMotionCost -->
