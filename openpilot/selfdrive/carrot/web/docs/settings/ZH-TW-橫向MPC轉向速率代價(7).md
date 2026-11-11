<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="LatMpcSteeringRateCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 橫向MPC轉向速率代價(7)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN LatMpcSteeringRateCost -->
<a id="LatMpcSteeringRateCost"></a>

## 橫向MPC轉向速率代價(7)

`LatMpcSteeringRateCost`

(車道模式) 轉向速率限制 — 值越低轉向越激進

<!-- CARROT:AUTO:BEGIN LatMpcSteeringRateCost -->
<!-- CARROT:AUTO:SOURCE facts="15aca23d88b872803c8c587f4fe2f535c4f6548db83339a93cea1f8650339243" semantic="abb62754276e8852ac2b76df32326edddc868ac4e65e04789efd359aa48f1f74" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `7`
- **範圍:** `0` ~ `1000`
- **步長:** `100`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcSteeringRateCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcSteeringRateCost -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（LaneMode）轉向速率限制：調低會讓轉向更積極。

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
<!-- CARROT:MANUAL:END LatMpcSteeringRateCost -->

<!-- CARROT:SETTING:END LatMpcSteeringRateCost -->
