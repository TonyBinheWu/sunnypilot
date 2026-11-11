<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="LatMpcInputOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 橫向MPC輸入偏移(4)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN LatMpcInputOffset -->
<a id="LatMpcInputOffset"></a>

## 橫向MPC輸入偏移(4)

`LatMpcInputOffset`

(車道模式) MPC 輸入補償 — 值越高進入彎道越早

<!-- CARROT:AUTO:BEGIN LatMpcInputOffset -->
<!-- CARROT:AUTO:SOURCE facts="c3e1126d313c367b3472d04774f2b74708d0b08684a0f1bcfc039b1318719c4e" semantic="efc63caea6708ae570390d3c639d780d27edaa7d333175c03cd31e82d16b81cf" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `4`
- **範圍:** `0` ~ `20`
- **步長:** `1`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcInputOffset -->

<!-- CARROT:MANUAL:BEGIN LatMpcInputOffset -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（LaneMode）MPC 輸入補償：調高會較早進入彎道。

- **調高：** 提前 MPC 輸入，較早回應彎道。
- **調低：** 延後對彎道的回應。
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
<!-- CARROT:MANUAL:END LatMpcInputOffset -->

<!-- CARROT:SETTING:END LatMpcInputOffset -->
