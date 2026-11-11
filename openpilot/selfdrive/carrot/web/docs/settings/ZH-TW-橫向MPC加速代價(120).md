<!-- CARROT:GENERATED schema="1" locale="zh-tw" group="STEER_LANEMODE" param="LatMpcAccelCost" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 橫向MPC加速代價(120)

**選單:** 駕駛控制 \> 轉向 \> 車道模式

---

<!-- CARROT:SETTING:BEGIN LatMpcAccelCost -->
<a id="LatMpcAccelCost"></a>

## 橫向MPC加速代價(120)

`LatMpcAccelCost`

(車道模式) 側向加速度限制 — 值越低靈活性越高但穩定性降低

<!-- CARROT:AUTO:BEGIN LatMpcAccelCost -->
<!-- CARROT:AUTO:SOURCE facts="d9c46b6b6aa6fe21e7a6ed304baeec10b9e6ccdad4b4fb598fba25f86f11223f" semantic="8538f6cbd23edf0ba7f4d95ad4afb9b20e5a66792ca42c8559874d43490b0ca6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **型別:** 數值
- **預設值:** `100`
- **範圍:** `0` ~ `500`
- **步長:** `10`
- **選單:** 駕駛控制 \> 轉向 \> 車道模式
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LatMpcAccelCost -->

<!-- CARROT:MANUAL:BEGIN LatMpcAccelCost -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 運作方式

（LaneMode）橫向加速度限制：調低可提高靈活度，但會降低穩定性。

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
<!-- CARROT:MANUAL:END LatMpcAccelCost -->

<!-- CARROT:SETTING:END LatMpcAccelCost -->
